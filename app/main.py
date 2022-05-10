import argparse
import logging
import sys

from chartparameters import DBParams
from charts import Chart

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

parser = argparse.ArgumentParser(description='datawarehouse visualization service')
parser.add_argument('--db-user', type=str, default="musterpraxis_dwh", help='use this user to connect to the dwh')
parser.add_argument('--db-password', type=str, default="password", help='use this password to connect to dwh')
parser.add_argument('--db-host', type=str, default="127.0.0.1", help="ipv4 or hostname of dwh")
parser.add_argument('--db-port', type=int, default=3306, help="connect to this port on the dwh")
parser.add_argument('--db-name', type=str, default="musterpraxis_dwh", help="use this database on the dwh")
args = parser.parse_args()

dbparams = DBParams(
    database=args.db_name,
    user=args.db_user,
    password=args.db_password,
    host=args.db_host,
    port=args.db_port)

queryparams = {"start_date": "2022-03-20", "end_date": "2022-03-28"}

#a = Chart("anzahl_neue_faelle_pro_tag", db_parameters=dbparams, query_parameters=queryparams)
a = Chart("durschnitt_alter_pro_sitzung", db_parameters=dbparams, query_parameters=queryparams)

a.get_bokeh_json()
