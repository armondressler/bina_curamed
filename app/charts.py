#class Chart:
#Query (mit parametern wie z.B. Zeit von / bis)
#Transformation query result zu columndatasource
#Definition bokeh figure (glyphs, annotations etc) -> evtl direkt als funktion definieren

import logging
from typing import Dict, List

from bokehfigures import CHART_COLLECTION, BokehFigure
from chartparameters import Database, DBQuery
from exceptions import ValidationError

log = logging.getLogger()

class Chart:
    collection = CHART_COLLECTION

    def __init__(self, name: str, database_parameters: Dict[str, str], query_parameters: Dict[str, str]):
        self.name = name
        self.collection_item = self._get_collection_item()
        self.database_parameters = database_parameters
        self.database_queries = self._get_database_queries()
        self.figure = self._get_figure()
        self._parameterize_database_queries(query_parameters)

    def _get_collection_item(self):
        collection_item = Chart.collection.get(self.name)
        if collection_item is None:
            raise ValidationError(f"Chart collection does not contain a key {self.name}")
        return collection_item

    def _parameterize_database_queries(self, parameters: dict):
        for _, query in self.database_queries.items():
            query.parameters = parameters

    def _get_database_queries(self) -> Dict[str, DBQuery]:
        dbqueries: Dict[str, DBQuery] = {}
        for data_source_name, data_source in self.collection_item.get("data_sources", {}).items():
            if isinstance(data_source, DBQuery):
                dbqueries[data_source_name] = data_source
        return dbqueries

    def _get_figure(self) -> type[BokehFigure]:
        return self.collection_item.get("figure")
        
    def _transform_query_result(self) -> None:
        for _, query in self.database_queries.items():
            query.transform_data()

    def _update_datasources(self):
        queries: List[DBQuery] = []
        for _, query in self.database_queries.items():
            queries.append(query)
        Database(**self.database_parameters).execute_queries(queries)

    def get_bokeh_json(self):
        self._update_datasources()
        self._transform_query_result()
        self.figure
        self.figure(data=self.database_queries)
