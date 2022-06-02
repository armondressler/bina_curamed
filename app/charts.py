import logging
from typing import Dict, List

from bokehfigures import (AnzahlNeueFaelleProTag, BokehFigure,
                          VerteilungAltersgruppenSitzungszeiten)
from datasources import Database, DBQuery
from exceptions import ValidationError
from transformers import ConvertToDateTypeTransformer

log = logging.getLogger()

class Chart:
    def __init__(self, figure: type[BokehFigure], database: Database|None=None, db_queries: Dict[str, DBQuery]={}, query_parameters: Dict[str, str]={}):
        self.figure = figure
        self.database: Database|None = database
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
                                                  required_parameters=("start_date", "end_date"))}
        super().__init__(AnzahlNeueFaelleProTag, database, database_queries, query_parameters)


class AgeGroupBySessionTime(Chart):
    def __init__(self, database: Database, query_parameters: Dict[str, str] = {}):
        database_queries = {"age_group_by_session_time": DBQuery(query="SELECT DATE_FORMAT(s.begin,'%H:%m:%S') AS date,TIMESTAMPDIFF(YEAR, p.birthDate, CURDATE()) AS age FROM session AS s JOIN patient AS p ON s.patient = p.id WHERE s.created BETWEEN %(start_date)s AND %(end_date)s;",
        required_parameters=("start_date", "end_date"),
        transformers=[ConvertToDateTypeTransformer(date_format="%H:%M:%S", date_column_name="date")])}
        super().__init__(VerteilungAltersgruppenSitzungszeiten, database, database_queries, query_parameters)
