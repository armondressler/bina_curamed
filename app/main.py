import argparse
import logging
import sys
from os import environ
import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import HTMLResponse

from charts import CasesPerDay, TurnoverPerMonth
from datasources import Database

__version__ = "1.0.0"

app = FastAPI()

parser = argparse.ArgumentParser(description='datawarehouse visualization service')
parser.add_argument('--port', type=int, default=8080, help="run api on this port")
parser.add_argument('--log-level', type=str, default="info", help="api log level", choices=["error","info","debug"])
parser.add_argument('--db-user', type=str, default=environ.get("DB_USER","musterpraxis_dwh"), help='use this user to connect to the dwh')
parser.add_argument('--db-password', type=str, default=environ.get("DB_PASSWORD", "password"), help='use this password to connect to dwh')
parser.add_argument('--db-host', type=str, default=environ.get("DB_HOST","127.0.0.1"), help="ipv4 or hostname of dwh")
parser.add_argument('--db-port', type=int, default=int(environ.get("DB_PORT", 3306)), help="connect to this port on the dwh")
parser.add_argument('--db-suffix', type=str, default=environ.get("DB_SUFFIX","_dwh"), help="append this to the database name before connecting")

args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.getLevelName(args.log_level.upper()))
log = logging.getLogger()

@app.get("/version")
async def root():
    return __version__

@app.get("/health")
def health():
    #TODO
    return {"status": "healthy"}

@app.get("/charts")
async def list_charts():
    return []

@app.get("/charts/{chart_id}")
async def render_chart(*,
                       chart_id: str = Path(max_length=32, regex="^[a-zA-Z][a-zA-Z0-9\\-]*$"),
                       customer: str = Query(max_length=32, regex="^[a-zA-Z][a-zA-Z0-9]*$"),
                       start_date: datetime.date,
                       end_date: datetime.date):

    database_name = customer + args.db_suffix if args.db_suffix else customer
    database = Database(user=args.db_user,
                        password=args.db_password,
                        host=args.db_host,
                        port=args.db_port,
                        database=database_name)
    query_parameters={"start_date": str(start_date), "end_date": str(end_date)}
    if chart_id == "cases-per-day":
        p = CasesPerDay(database=database, query_parameters=query_parameters)
    elif chart_id == "turnover-per-month":
        p = TurnoverPerMonth(database=database, query_parameters=query_parameters)
    else:
        raise HTTPException(status_code=404, detail="Chart not found")
    return p.get_bokeh_json()

@app.get("/dashboards")
async def list_dashboards():
    return []

@app.get("/dashboards")
async def dashboard(*, dashboard_id: str):
    return []

@app.get("/home", response_class=HTMLResponse)
async def home():
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
    const response = await fetch('/charts/turnover-per-month?customer=musterpraxis&start_date=2021-09-01&end_date=2022-03-31')
    const item = await response.json()
    Bokeh.embed.embed_item(item, "myplot")
    }
    run();
    </script>
    </body>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=args.port, log_level=args.log_level)
