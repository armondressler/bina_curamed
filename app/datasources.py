import logging
from typing import List

import mariadb
import pandas as pd

from exceptions import QueryResultTransformationError, ValidationError
from transformers import DBQueryResultsTransformer

log = logging.getLogger()

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
        except mariadb.ProgrammingError as err:
            log.error(f"Failed after connection: {err}")
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
