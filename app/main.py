import argparse
import logging
import sys
from os import environ

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import uvicorn

from charts import Chart

__version__ = "1.0.0"

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

parser = argparse.ArgumentParser(description='datawarehouse visualization service')
parser.add_argument('--port', type=int, default=8080, help="run api on this port")
parser.add_argument('--log-level', type=str, default="info", help="api log level", choices=["error","info","debug"])
parser.add_argument('--db-user', type=str, default=environ.get("DB_USER","musterpraxis_dwh"), help='use this user to connect to the dwh')
parser.add_argument('--db-password', type=str, default=environ.get("DB_PASSWORD", "password"), help='use this password to connect to dwh')
parser.add_argument('--db-host', type=str, default=environ.get("DB_HOST","127.0.0.1"), help="ipv4 or hostname of dwh")
parser.add_argument('--db-port', type=int, default=int(environ.get("DB_PORT", 3306)), help="connect to this port on the dwh")
parser.add_argument('--db-name', type=str, default=environ.get("DB_NAME","musterpraxis_dwh"), help="use this database on the dwh")
args = parser.parse_args()

database_parameters = {
    "database": args.db_name,
    "user": args.db_user,
    "password": args.db_password,
    "host": args.db_host,
    "port": args.db_port}

queryparams = {"start_date": "2022-03-20", "end_date": "2022-03-28"}

app = FastAPI()

@app.get("/version")
async def root():
    return __version__

@app.get("/charts")
async def list_charts():
    return []

@app.get("/charts/{chart_id}")
async def render_chart(*, chart_id: int):
    import json
    from bokeh.plotting import figure
    from bokeh.embed import json_item
    p = figure()
    p.circle([1,2,3,4], [4,3,2,1])
    return json_item(p)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    from bokeh.resources import CDN
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>""" + CDN.render() + """
    </head>
    <body>
    <div id="myplot"></div>
    <script>
    async function run() {
    const response = await fetch('/charts/1')
    const item = await response.json()
    Bokeh.embed.embed_item(item, "myplot")
    }
    run();
    </script>
    </body>
    """

"""
    fetch('/charts/1')
    .then(function(response) { return response.json(); })
    .then(function(item) { return Bokeh.embed.embed_item(item, 'myplot'); })
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=args.port, log_level=args.log_level)

#a = Chart("anzahl_neue_faelle_pro_tag", database_parameters=database_parameters, query_parameters=queryparams)
#a = Chart("altersgruppe_sitzung_pro_tageszeit", database_parameters=database_parameters, query_parameters=queryparams)

#a.get_bokeh_json()
