#class Chart:
#Query (mit parametern wie z.B. Zeit von / bis)
#Transformation query result zu columndatasource
#Definition bokeh figure (glyphs, annotations etc) -> evtl direkt als funktion definieren

import logging

import mariadb
from chartparameters import CHART_COLLECTION, DBParams
from exceptions import ValidationError

log = logging.getLogger()

class Chart:
    collection = CHART_COLLECTION

    def __init__(self, name, db_parameters: DBParams, query_parameters: dict =None):
        self.name = name
        self.db_parameters = db_parameters
        self.query_result_transformers = self._get_query_result_transformers()
        self.query_parameters = self._ensure_required_query_parameters(query_parameters)
        self.db_query = self._get_db_query()
        self.figure = self._get_figure()
        self.query_result = {}

    def _get_db_query(self):
        collection_item = Chart.collection.get(self.name)
        if collection_item is None:
            raise ValidationError(f"Chart collection does not contain a key {self.name}")
        return collection_item.get("dbquery").query

    def _get_figure(self):
        collection_item = Chart.collection.get(self.name)
        return collection_item.get("figure")

    def _get_query_result_transformers(self):
        collection_item = Chart.collection.get(self.name)
        return collection_item.get("transformers")

    def _ensure_required_query_parameters(self, query_parameters):
        """We want to instanciate Chart with query parameters as a dict to ensure all the required parameters are present.
        However the execution of the query on the actual db just needs a tuple of the dict values.
        """
        for required_parameter in Chart.collection.get(self.name).get("dbquery").required_parameters:
            if required_parameter not in query_parameters:
                raise ValidationError(f"Required parameter {required_parameter} not present")
        return query_parameters

    def _transform_to_columndata_dict(self, columns, data):
        """create dict as expected by bokeh with keys being names of the column and value being a list of its values"""
        query_result_dict = {}
        for index, column in enumerate(columns):
            query_result_dict[column] = [tup[index] for tup in data]
        return query_result_dict

    def _query_database(self):
        try:
            conn = mariadb.connect(**self.db_parameters.as_dict())
        except mariadb.Error as e:
            log.error(f"Failed to connect to database: {e}")
            raise
        cur = conn.cursor()
        log.debug(f"Running query: \"{self.db_query}\" with parameters {self.query_parameters}")
        cur.execute(self.db_query, self.query_parameters)
        columns = [column_descriptor[0] for column_descriptor in cur.description]
        data = cur.fetchall()
        self.query_result = self._transform_to_columndata_dict(columns=columns, data=data)
        conn.close()

    def _transform_query_result(self):
        if self.query_result_transformers is None:
            return
        for transformer in self.query_result_transformers:
            self.query_result = transformer.transform(self.query_result)

    def get_bokeh_json(self):
        self._query_database()
        self._transform_query_result()
        print(self.query_result)
        self.figure(data=self.query_result)
