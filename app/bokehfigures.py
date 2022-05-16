import enum
from operator import index
from typing import Dict
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.embed import json_item
from bokeh.palettes import GnBu3
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap

from chartparameters import ConvertToHistogramTransformer, DBQuery, ConvertToDateTypeTransformer

import numpy as np

class BokehFigure:
    def __init__(self, data: Dict[str, DBQuery]):
        self.data = data
        self.figure = self.setup_figure()

    def as_json(self):
        #return json_item(self.figure)
        pass

    def setup_figure(self):
        pass


class AnzahlNeueFaelleProTag(BokehFigure):
    def setup_figure(self):
        df = self.data["anzahl_neue_faelle_pro_tag"].dataframe
        p = figure(title="Neue Fälle pro Tag", y_axis_label="Neue Fälle", x_range=df.get("date"))
        p.vbar(x=df.get("date"), top=df.get("cases"), color="green", width=0.8)
        #p.line(x=self.data.get("date"), y=self.data.get("cases"), color="green")
        p.yaxis.minor_tick_out = 0
        show(p)

class VerteilungAltersgruppenSitzungszeiten(BokehFigure):
    def setup_figure(self):
        df = self.data["altersgruppe_sitzung_pro_tageszeit"].dataframe
        df["date"] = df["date"].dt.hour
        hist, xedges, yedges = np.histogram2d(df["date"],df["age"],bins=[[0,10,12,15,24],[0,18,40,65,80,120]])
        timeintervals = [f"{low}:00 - {high}:00" for low,high in zip(xedges[:-1],xedges[1:])]
        ageintervals = [f"{low} - {high}" for low,high in zip(yedges[:-1],yedges[1:])]

        TOOLTIPS = [
            ("Zeitintervall", "$y"),
            ("Anzahl Sitzungen", "@age"),
        ]
        p = figure(title="Verteilung von Altersgruppen auf Sitzungszeiten", y_axis_label="Uhrzeit", x_axis_label="Anzahl Sitzungen", tooltips=TOOLTIPS, y_range=timeintervals)
        p.ygrid.grid_line_color = None
        
        data = {}
        for timeindex,timeinterval in enumerate(timeintervals):
            a = list(hist[timeindex])
            data["left"] = [0] + [sum(a[:index+1]) for index in range(len(a)-1)]    
            data["right"] = [sum(a[:index+1]) for index in range(len(a))]
            data["age"] = ageintervals
            color_slice = slice(0,len(ageintervals))
            data["color"] = Spectral6[color_slice]
            data["legend_label"] = ageintervals
            data["y"] = [(name,index) for name,index in zip([timeinterval]*len(a),[timeindex]*len(a))]
            print(data)
            p.hbar(y="y", left="left", right="right", height=0.75, fill_color="color", source=ColumnDataSource(data), legend_field="legend_label")
        show(p)
        


CHART_COLLECTION = {
    "anzahl_neue_faelle_total": {
        "data_sources": {
            "anzahl_neue_faelle_total": DBQuery(query="SELECT count(*) as cases FROM `case` WHERE created BETWEEN %(start_date)s AND %(end_date)s;",
                                                required_parameters=("start_date", "end_date"))
        },
        "figure": AnzahlNeueFaelleProTag,
    },
    "anzahl_neue_faelle_pro_tag": {
        "data_sources": {
            "anzahl_neue_faelle_pro_tag": DBQuery(query="WITH recursive date_ranges AS (select %(start_date)s as date union all select date + interval 1 day from date_ranges where date < %(end_date)s) select date,COALESCE(cases, 0) as cases from date_ranges as a left join ( SELECT count(*) as cases,DATE_FORMAT(created,'%Y-%m-%d') as date2 FROM `case` WHERE created BETWEEN %(start_date)s AND %(end_date)s GROUP BY DATE_FORMAT(created,'%Y-%m-%d')) as b  on a.date = b.date2;", 
                                                  required_parameters=("start_date", "end_date"))
        },
        "figure": AnzahlNeueFaelleProTag,
    },
    "altersgruppe_sitzung_pro_tageszeit": {
        "data_sources": {
            "altersgruppe_sitzung_pro_tageszeit": DBQuery(query="SELECT DATE_FORMAT(s.begin,'%H:%m:%S') AS date,TIMESTAMPDIFF(YEAR, p.birthDate, CURDATE()) AS age FROM session AS s JOIN patient AS p ON s.patient = p.id WHERE s.created BETWEEN %(start_date)s AND %(end_date)s;",
                                                          required_parameters=("start_date", "end_date"),
                                                          transformers=[
                                                              ConvertToDateTypeTransformer(date_format="%H:%M:%S", date_column_name="date"),
                                                              #ConvertToHistogramTransformer(column_name="age",bins=[0,10,18,40,65,85,120]),
                                                              ])
        },
        "figure": VerteilungAltersgruppenSitzungszeiten
    }
}