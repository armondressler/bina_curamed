from typing import Dict

import numpy as np
import pandas as pd
from bokeh.embed import json_item
from bokeh.palettes import Spectral6
from bokeh.plotting import ColumnDataSource, figure
from bokeh.models import HoverTool

from datasources import DBQuery


class BokehFigure:
    def __init__(self, data: Dict[str, DBQuery]):
        self.data = data
        self.figure = self.setup_figure()

    def as_json(self):
        return json_item(self.figure)

    def setup_figure(self):
        return figure()


class AnzahlNeueFaelleProTag(BokehFigure):
    def setup_figure(self):
        df = self.data["cases_per_day"].dataframe
        tooltips = [
            ("Anzahl Fälle", "@top"),
        ]
        print(df.shape)
        p = figure(title="Neue Fälle pro Tag",
                   y_axis_label="Neue Fälle",
                   tooltips=tooltips,
                   x_axis_type="datetime")
        p.vbar(x=df.get("date"), top=df.get("cases"), color="green", width=64_000_000)
        p.yaxis.minor_tick_out = 0
        return p

class VerteilungAltersgruppenSitzungszeiten(BokehFigure):
    def setup_figure(self):
        df = self.data["altersgruppe_sitzung_pro_tageszeit"].dataframe
        df["date"] = df["date"].dt.hour
        hist, xedges, yedges = np.histogram2d(df["date"],df["age"],bins=[[0,10,12,15,24],[0,18,40,65,80,120]])
        timeintervals = [f"{low}:00 - {high}:00" for low,high in zip(xedges[:-1],xedges[1:])]
        ageintervals = [f"{low} - {high}" for low,high in zip(yedges[:-1],yedges[1:])]

        tooltips = [
            ("Altersgruppe", "@age"),
            ("Anzahl Sitzungen", "@count"),
        ]
        p = figure(title="Verteilung von Altersgruppen auf Sitzungszeiten", y_axis_label="Uhrzeit", x_axis_label="Anzahl Sitzungen", tooltips=tooltips)
        p.ygrid.grid_line_color = None
        
        data = {}
        for timeindex,timeinterval in enumerate(timeintervals):
            a = list(hist[timeindex])
            data["left"] = [0] + [sum(a[:index+1]) for index in range(len(a)-1)]    
            data["right"] = [sum(a[:index+1]) for index in range(len(a))]
            data["count"] = a
            data["age"] = ageintervals
            color_slice = slice(0,len(ageintervals))
            data["color"] = Spectral6[color_slice]
            data["legend_label"] = ageintervals
            data["y"] = [timeindex] * len(a)
            p.yaxis.major_label_overrides[timeindex] = timeinterval
            p.legend.title = 'Altersgruppen'
            print(data)
            if timeindex == 0:
                p.hbar(y="y", left="left", right="right", height=0.75, fill_color="color", source=ColumnDataSource(data), legend_group="legend_label")
            else:
                p.hbar(y="y", left="left", right="right", height=0.75, fill_color="color", source=ColumnDataSource(data))
        return p

#TODO Nur invoices mit invStat paid sollten als Umsatz gezählt werden, mangels Daten in musterpraxis vorerst weggelassen -> where invStat = "paid";
#TODO combinedName ungünstiger Schlüssel bei gleichnamigen Dr... -> executingDoctor verwenden?
class TurnoverPerMonthFigure(BokehFigure):
    def setup_figure(self):
        from bokeh.palettes import brewer
        turnover_by_executing_doctor = self.data["turnover_by_executing_doctor"].dataframe
        executing_doctors = turnover_by_executing_doctor["combinedName"].drop_duplicates().dropna()
        df_split_by_personnel = pd.DataFrame()
        df_split_by_personnel["date"] = turnover_by_executing_doctor["date"].drop_duplicates()
        for combinedName in executing_doctors:
            df_split_by_personnel[combinedName] = pd.merge(df_split_by_personnel, turnover_by_executing_doctor[turnover_by_executing_doctor["combinedName"] == combinedName], on="date", how="outer")["SumTotalAmount"].fillna(0)

        """ daily_turnover_summary = self.data["turnover_per_day"].dataframe
        monthly_turnover_summary = daily_turnover_summary.groupby(daily_turnover_summary.date.dt.to_period('M'))['SumCalcAmtTotal'].sum()
        hover = HoverTool(names=["monthly_turnover_vbar"], tooltips=[("Umsatz in SFr", "@top{0.00}")])
        p = figure(title="Umsatz pro Monat",
                   y_axis_label="Umsatz in SFr",
                   x_axis_type="datetime",
                   tools=['pan', 'box_zoom', 'wheel_zoom', 'save','reset', hover])
        p.vbar(x=monthly_turnover_summary.index, top=monthly_turnover_summary, name="monthly_turnover_vbar", color="green", width=64_000_000 * 30, fill_alpha=0.5)
        p.line(daily_turnover_summary.get("date"), daily_turnover_summary.get("SumCalcAmtTotal"))
        p.yaxis.minor_tick_out = 0 """
        print(df_split_by_personnel.columns)
        hover = HoverTool(names=[c for c in executing_doctors], tooltips=[('Datum', '@date{%F}'),("Name","$name"),("Umsatz","@$name SFr")], formatters={'@date': 'datetime'})
        p = figure(title="Umsatz pro Arzt",x_axis_type="datetime", tools=['pan', 'box_zoom', 'wheel_zoom', 'save','reset', hover])
        p.varea_stack([c for c in executing_doctors],
                      x='date',
                      color=brewer['Spectral'][executing_doctors.count()],
                      legend_label=[c for c in executing_doctors],
                      name=[c for c in executing_doctors],
                      source=df_split_by_personnel)
        return p