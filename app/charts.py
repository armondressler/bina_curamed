#class Chart:
#Query (mit parametern wie z.B. Zeit von / bis)
#Transformation query result zu columndatasource
#Definition bokeh figure (glyphs, annotations etc) -> evtl direkt als funktion definieren

from dataclasses import dataclass
import logging

import mariadb

log = logging.getLogger()

@dataclass
class DBParams:
    database: str
    user: str
    password: str
    host: str
    port: int

class Chart:
    def __init__(self, name, dbparams, start_date=None, end_date=None):
        self.name = name
        self.dbparams = dbparams
        self.start_date = start_date
        self.end_date = end_date
        self.query_result = None
    
    def _get_dbquery(self):
        pass


    def _query_database(self):
        try:
            conn = mariadb.connect(**self.dbparams)
        except mariadb.Error as e:
            log.error(f"Failed to connect to database: {e}")
            raise

        cur = conn.cursor()
        cur.execute()

        for row in cur:
            log.info(row)


    def get_bokeh_json():
        pass
