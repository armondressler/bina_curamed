import argparse
import logging
import sys
from socket import timeout

import mariadb

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

parser = argparse.ArgumentParser(description='datawarehouse visualization service')
parser.add_argument('--db-user', type=str, default="musterpraxis_dwh", help='use this user to connect to the dwh')
parser.add_argument('--db-password', type=str, default="password", help='use this password to connect to dwh')
parser.add_argument('--db-host', type=str, default="127.0.0.1", help="ipv4 or hostname of dwh")
parser.add_argument('--db-port', type=int, default=3306, help="connect to this port on the dwh")
parser.add_argument('--db-name', type=str, default="musterpraxis_dwh", help="use this database on the dwh")
args = parser.parse_args()

DB_PASSWORD = "password"
DB_NAME = "musterpraxis_dwh"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
 #DB_CONNSTRING = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    conn = mariadb.connect(
        user=args.db_user,
        password=args.db_password,
        host=args.db_host,
        port=args.db_port,
        database=args.db_name)
except mariadb.Error as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("SELECT created, lastName FROM patient ORDER BY created LIMIT 10")

for row in cur:
    log.info(row)
