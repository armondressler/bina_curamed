import logging
from typing import Dict, List, Optional

from bokehfigures import (AnzahlNeueFaelleProTag,
                          BenefitsByInvoiceStatusPerDayFigure, BokehFigure,
                          TurnoverByServiceTypeFigure, TurnoverPerMonthFigure,
                          VerteilungAltersgruppenSitzungszeiten)
from datasources import Database, DBQuery
from exceptions import ValidationError
from transformers import (ConvertToDateTypeTransformer,
                          FillDateGapsTransformer, RoundFloatTypeTransformer)

log = logging.getLogger()

class Chart:
    def __init__(self, figure: type[BokehFigure], database: Optional[Database]=None, db_queries: Dict[str, DBQuery]={}, query_parameters: Dict[str, str]={}):
        self.figure = figure
        self.database: Optional[Database] = database
        self.database_queries = db_queries
        self._parameterize_database_queries(query_parameters)

    def _parameterize_database_queries(self, parameters: dict):
        for _, query in self.database_queries.items():
            query.parameters = parameters
        
    def _transform_query_result(self) -> None:
        for _, query in self.database_queries.items():
            query.transform_data()

    def _update_datasources(self):
        queries: List[DBQuery] = []
        for _, query in self.database_queries.items():
            queries.append(query)
        if queries:
            if self.database is None:
                raise ValidationError(f"Missing database parameters for chart")
            else:
                self.database.execute_queries(queries)

    def get_bokeh_json(self):
        self._update_datasources()
        self._transform_query_result()
        return self.figure(data=self.database_queries).as_json()
        
#table of dates from start day to end day
#WITH recursive date_ranges AS (select '2022-03-01' as date union all select date + interval 1 day from date_ranges where date < '2022-03-30') select date from date_ranges;


class CasesTotal(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"cases_total": DBQuery(query="SELECT count(*) as cases FROM `case` WHERE created BETWEEN %(start_date)s AND %(end_date)s;",
                                          required_parameters=("start_date", "end_date"))}
        super().__init__(AnzahlNeueFaelleProTag,
                         database,
                         database_queries,
                         query_parameters)
            
class CasesPerDay(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"cases_per_day": DBQuery(query="WITH recursive date_ranges AS (select %(start_date)s as date union all select date + interval 1 day from date_ranges where date < %(end_date)s) select date,COALESCE(cases, 0) as cases from date_ranges as a left join ( SELECT count(*) as cases,DATE_FORMAT(created,'%Y-%m-%d') as date2 FROM `case` WHERE created BETWEEN %(start_date)s AND %(end_date)s GROUP BY DATE_FORMAT(created,'%Y-%m-%d')) as b  on a.date = b.date2;", 
                                                  required_parameters=("start_date", "end_date"),
                                                  transformers=[ConvertToDateTypeTransformer()])}
        super().__init__(AnzahlNeueFaelleProTag, database, database_queries, query_parameters)


class AgeGroupBySessionTime(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"age_group_by_session_time": DBQuery(query="SELECT DATE_FORMAT(s.begin,'%H:%m:%S') AS date,TIMESTAMPDIFF(YEAR, p.birthDate, CURDATE()) AS age FROM session AS s JOIN patient AS p ON s.patient = p.id WHERE s.created BETWEEN %(start_date)s AND %(end_date)s;",
        required_parameters=("start_date", "end_date"),
        transformers=[ConvertToDateTypeTransformer(date_format="%H:%M:%S", date_column_name="date")])}
        super().__init__(VerteilungAltersgruppenSitzungszeiten, database, database_queries, query_parameters)

class TurnoverPerMonth(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"turnover_per_day": DBQuery(query="WITH RECURSIVE date_ranges AS (SELECT %(start_date)s AS date UNION ALL SELECT date + interval 1 day FROM date_ranges WHERE date < %(end_date)s) SELECT date,COALESCE(SumCalcAmtTotal, 0) AS SumCalcAmtTotal FROM date_ranges AS calendar LEFT JOIN (SELECT SUM(CalcAmtTotal) AS SumCalcAmtTotal,DATE_FORMAT(created,'%Y-%m-%d') AS date2 FROM invoice WHERE (created BETWEEN %(start_date)s AND %(end_date)s) AND (traStat = 'transferred' OR trastat = 'dispatched') GROUP BY DATE_FORMAT(created,'%Y-%m-%d')) AS billing ON calendar.date = billing.date2;",
                                                        required_parameters=("start_date", "end_date"),
                                                        transformers=[ConvertToDateTypeTransformer(date_column_name="date"),
                                                                      RoundFloatTypeTransformer("SumCalcAmtTotal", digit_count=2)]),
                            "turnover_by_executing_doctor": DBQuery(query="SELECT DATE_FORMAT(`date`,'%Y-%m-%d') AS date,SUM(totalAmount) AS SumTotalAmount,SUM(totalTar) AS SumTotalTar,SUM(totalTar2) AS SumTotalTar2,SUM(totalMedication) as SumTotalMedication,SUM(totalMigel) AS SumTotalMigel,SUM(totalAnalysis) AS SumTotalAnalysis,SUM(totalPhysio) AS SumTotalPhysio, SUM(totalMisc) AS SumTotalMisc,SUM(totalOther) AS SumTotalOther,s.executingDoctor,CONCAT(IFNULL(p.firstName, ''), ' ', IFNULL(p.lastName,'')) AS combinedName FROM invoicePart AS invp JOIN session AS s ON invp.session = s.id JOIN personnel AS p ON s.executingDoctor = p.id JOIN invoice AS inv ON invp.invoice = inv.id WHERE (invp.invoice != 'aaaaaaaaaaaaaaaaaaaa') AND (inv.created BETWEEN %(start_date)s AND %(end_date)s) GROUP BY DATE_FORMAT(`date`,'%Y-%m-%d'),executingDoctor;",
                                                           required_parameters=("start_date", "end_date"),
                                                           transformers=[ConvertToDateTypeTransformer(date_column_name="date"),
                                                                         FillDateGapsTransformer(date_column_name="date")])}
        super().__init__(TurnoverPerMonthFigure, database, database_queries, query_parameters)

class BenefitsByInvoiceStatusPerDay(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"benefits_by_invoice_status": DBQuery(query="SELECT DATE_FORMAT(bc.created,'%Y-%m-%d') AS date, bc.effCalcAmtVat, inv.invStat FROM benefitCombined AS bc JOIN invoice AS inv ON bc.invoice = inv.id WHERE bc.invoice != 'aaaaaaaaaaaaaaaaaaaa' AND (inv.traStat = 'transferred' OR inv.traStat = 'dispatched') AND bc.created BETWEEN %(start_date)s AND %(end_date)s;",
                                                                  required_parameters=("start_date", "end_date"),
                                                                  transformers=[ConvertToDateTypeTransformer(date_column_name="date"),
                                                                                FillDateGapsTransformer(date_column_name="date",nan_fill={"effCalcAmtVat": 0, "invStat": "paid"})])}
        super().__init__(BenefitsByInvoiceStatusPerDayFigure, database, database_queries, query_parameters)

class TurnoverByServiceType(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"turnover_by_service_type_per_day": DBQuery(query="SELECT DATE_FORMAT(`date`,'%Y-%m-%d') AS date,SUM(totalAmount) AS SumTotalAmount,SUM(totalTar) AS SumTotalTar,SUM(totalTar2) AS SumTotalTar2,SUM(totalMedication) as SumTotalMedication,SUM(totalMigel) AS SumTotalMigel,SUM(totalAnalysis) AS SumTotalAnalysis,SUM(totalPhysio) AS SumTotalPhysio, SUM(totalMisc) AS SumTotalMisc,SUM(totalOther) AS SumTotalOther FROM invoicePart AS invp JOIN invoice AS inv ON invp.invoice = inv.id WHERE (invp.invoice != 'aaaaaaaaaaaaaaaaaaaa') AND (inv.created BETWEEN %(start_date)s AND %(end_date)s) GROUP BY DATE_FORMAT(`date`,'%Y-%m-%d')",
                                                       required_parameters=("start_date", "end_date"),
                                                        transformers=[ConvertToDateTypeTransformer(date_column_name="date"),
                                                                      FillDateGapsTransformer(date_column_name="date",nan_fill={"SumTotalAmount":0.0,
                                                                                                                                "SumTotalTar": 0.0,
                                                                                                                                "SumTotalTar2": 0.0,
                                                                                                                                "SumTotalMedication": 0.0,
                                                                                                                                "SumTotalMigel": 0.0,
                                                                                                                                "SumTotalAnalysis": 0.0,
                                                                                                                                "SumTotalPhysio": 0.0,
                                                                                                                                "SumTotalMisc": 0.0,
                                                                                                                                "SumTotalOther": 0.0 })])}
        super().__init__(TurnoverByServiceTypeFigure, database, database_queries, query_parameters)
