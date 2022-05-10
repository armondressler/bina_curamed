from dataclasses import dataclass, asdict
import logging
from exceptions import QueryResultTransformationError

from bokehfigures import AnzahlNeueFaelleProTag, DurchschnittAlterProSitzung

log = logging.getLogger()

@dataclass
class DBParams:
    database: str
    user: str
    password: str
    host: str
    port: int

    def as_dict(self):
        return asdict(self)

@dataclass
class DBQuery:
    query: str
    required_parameters: tuple

class DBQueryResultsTransformer:
    def transform(self, query_result):
        log.warning(f"Missing transform method for {type(self)}")
        raise QueryResultTransformationError(f"Missing transform method for {type(self)}")

class ConvertToDateTypeTransformer(DBQueryResultsTransformer):
    def __init__(self, date_format="%Y-%m-%d", date_column_name="date"):
        self.date_format = date_format
        self.date_column_name = date_column_name

    def transform(self, query_result):
        from datetime import datetime
        datecolumn = query_result.get(self.date_column_name)
        if datecolumn is None:
            raise QueryResultTransformationError(f"Column {self.date_column_name} missing in query result data (available: {query_result.keys().join(', ')})")   
        
        query_result[self.date_column_name] = [datetime.strptime(d, '%Y-%m-%d') for d in datecolumn]
        return query_result

class FillDateGapsTransformer(DBQueryResultsTransformer):
    def __init__(self, date_column_name="date", gappable_column_name="cases", fill_gaps_with_value=0):
        self.date_column_name = date_column_name
        self.gappable_column_name = gappable_column_name
        self.fill_gaps_with_value = fill_gaps_with_value

    def transform(self, query_result: dict):
        from datetime import timedelta
        datecolumn = query_result.get(self.date_column_name)
        if datecolumn is None:
            raise QueryResultTransformationError(f"Column {self.date_column_name} missing in query result data (available: {query_result.keys().join(', ')})")
        print(datecolumn[0], type(datecolumn[0]))

        start_date = datecolumn[0]
        end_date = datecolumn[-1]

        delta = end_date - start_date
        if not isinstance(delta, timedelta):
            raise QueryResultTransformationError(f"Values in column {self.date_column_name} are not of type date ({type(start_date)})")

        gappable_column = query_result.get(self.gappable_column_name)
        if gappable_column is None:
            raise QueryResultTransformationError(f"Column {self.gappable_column_name} to be gapped with {self.fill_gaps_with_value} missing in query result data (available: {self.query_result.keys().join(', ')})")

        new_datecolumn = [] #its getting late
        new_gappable_column = []
        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            print(f"i is {i}")
            if day in datecolumn:
                continue
            datecolumn[i] = day
            gappable_column[i] = self.fill_gaps_with_value
        
        query_result[self.date_column_name] = datecolumn
        query_result[gappable_column] = gappable_column

        return query_result


        

CHART_COLLECTION = {
    "anzahl_neue_faelle_total": {
        "dbquery": DBQuery(
            query="SELECT count(*) as cases FROM `case` WHERE created BETWEEN ? AND ?;",
            required_parameters=("start_date", "end_date")
        ),

    },
    "anzahl_neue_faelle_pro_tag": {
        "dbquery": DBQuery(
            query="WITH recursive date_ranges AS (select %(start_date)s as date union all select date + interval 1 day from date_ranges where date < %(end_date)s) select date,COALESCE(cases, 0) as cases from date_ranges as a left join ( SELECT count(*) as cases,DATE_FORMAT(created,'%Y-%m-%d') as date2 FROM `case` WHERE created BETWEEN %(start_date)s AND %(end_date)s GROUP BY DATE_FORMAT(created,'%Y-%m-%d')) as b  on a.date = b.date2;",
            required_parameters=("start_date", "end_date")
        ),
        "figure": AnzahlNeueFaelleProTag,
        "transformers": [
            #ConvertToDateTypeTransformer(date_column_name="date")
        ]
    },
    "altersgruppe_sitzung_pro_tageszeit": {
        "dbquery": DBQuery(
            query="SELECT TIMESTAMPDIFF(YEAR, p.birthDate, CURDATE()) AS age FROM session AS s JOIN patient AS p ON s.patient = p.id WHERE s.created BETWEEN %(start_date)s AND %(end_date)s;",
            required_parameters=("start_date", "end_date")
        ),
        "figure": DurchschnittAlterProSitzung
    }
}