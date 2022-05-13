import logging
from typing import List

import mariadb
import numpy as np
import pandas as pd

from exceptions import QueryResultTransformationError, ValidationError

log = logging.getLogger()


class DBQueryResultsTransformer:
    def transform(self, query_result):
        log.warning(f"Missing transform method for {type(self)}")
        raise QueryResultTransformationError(f"Missing transform method for {type(self)}")

class DBQuery:
    def __init__(self, query: str, required_parameters: tuple, transformers: None|List[DBQueryResultsTransformer] = None):
        self.query = query
        self.required_parameters = required_parameters
        self.transformers = transformers or []
        self.columns: List[str] = []
        self.data = []
        self._dataframe: pd.DataFrame = pd.DataFrame()
        self._parameters = {}

    @property
    def parameters(self) -> dict:
        return self._parameters

    @parameters.setter
    def parameters(self, params: dict) -> None:
        missing_required_parameters = set(self.required_parameters).difference(params)
        if missing_required_parameters:
            raise ValidationError(f"Missing parameter(s): {', '.join(missing_required_parameters)}")
        self._parameters = params

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._dataframe.empty:
            self._dataframe = self._to_dataframe(self.data, self.columns)
        return self._dataframe

    @dataframe.setter
    def dataframe(self, frame: pd.DataFrame):
        self._dataframe = frame

    def transform_data(self):
        for transformer in self.transformers:
            log.debug(f"Running transformer {self.__class__}")
            self.dataframe = transformer.transform(self.dataframe)

    def _to_dataframe(self, data: list, columns: List[str]) -> pd.DataFrame:
        try:
            frame = pd.DataFrame(data, columns=columns)
        except ValueError as err:
            raise QueryResultTransformationError(f"Failed to transform mariadb query result into pandas dataframe: {err}")
        return frame

class Database:
    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def execute_queries(self, queries: List[DBQuery]) -> None:
        try:
            conn = mariadb.connect(user=self.user,
                                   password=self.password,
                                   host=self.host,
                                   port=self.port,
                                   database=self.database)
        except mariadb.Error as err:
            log.error(f"Failed to connect to database: {err}")
            raise
        cur = conn.cursor()
        for query in queries:
            log.debug(f"Running query: \"{query.query}\" with parameters {query.parameters}")
            cur.execute(query.query, query.parameters)
            columns = [column_descriptor[0] for column_descriptor in cur.description]
            data = cur.fetchall()
            log.debug(f"Query data: {data}")
            log.debug(f"Query columns: {columns}")
            query.columns, query.data = columns, data
        conn.close()


class ConvertToDateTypeTransformer(DBQueryResultsTransformer):
    def __init__(self, date_format="%Y-%m-%d", date_column_name="date"):
        self.date_format = date_format
        self.date_column_name = date_column_name

    def transform(self, dataframe: pd.DataFrame):
        dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name], format=self.date_format)
        return dataframe

class ConvertToHistogramTransformer(DBQueryResultsTransformer):
    """Return distribution of pandas column column_name into bins with a new dataframe with columns count, left, right"""
    def __init__(self, column_name, bins):
        self.column_name = column_name
        self.bins = bins

    def transform(self, dataframe):
        values, bins = np.histogram(dataframe.get(self.column_name), bins=self.bins)
        return pd.DataFrame({"count": values, "left": [b for b in bins[:-1]], "right": [b for b in bins[1:]]})

class FillDateGapsTransformer(DBQueryResultsTransformer):
    def __init__(self, date_column_name="date", gappable_column_name="cases", fill_gaps_with_value=0):
        self.date_column_name = date_column_name
        self.gappable_column_name = gappable_column_name
        self.fill_gaps_with_value = fill_gaps_with_value

    def transform(self, query_result: dict):
        from datetime import timedelta
        datecolumn = query_result.get(self.date_column_name)
        if datecolumn is None:
            raise QueryResultTransformationError(f"Column {self.date_column_name} missing in query result data (available: ???)")
        start_date = datecolumn[0]
        end_date = datecolumn[-1]

        delta = end_date - start_date
        if not isinstance(delta, timedelta):
            raise QueryResultTransformationError(f"Values in column {self.date_column_name} are not of type date ({type(start_date)})")

        gappable_column = query_result.get(self.gappable_column_name)
        if gappable_column is None:
            raise QueryResultTransformationError(f"Column {self.gappable_column_name} to be gapped with {self.fill_gaps_with_value} missing in query result data (available: ???)")

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            if day in datecolumn:
                continue
            datecolumn[i] = day
            gappable_column[i] = self.fill_gaps_with_value
        
        query_result[self.date_column_name] = datecolumn
        query_result[gappable_column] = gappable_column

        return query_result

