from calendar import month
from typing import Dict

import numpy as np
import pandas as pd
from bokeh.embed import json_item
from bokeh.models import HoverTool
from bokeh.palettes import Spectral6, brewer
from bokeh.plotting import ColumnDataSource, figure

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
        p = figure(title="Neue Fälle pro Tag",
                   y_axis_label="Neue Fälle",
                   tooltips=tooltips,
                   x_axis_type="datetime")
        p.toolbar.logo = None  # type: ignore

        p.vbar(x=df.get("date"),
               top=df.get("cases"),
               color="green",
               width=64_000_000)
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
        p = figure(title="Verteilung von Altersgruppen auf Sitzungszeiten",
                   y_axis_label="Uhrzeit",
                   x_axis_label="Anzahl Sitzungen",
                   tooltips=tooltips)
        p.toolbar.logo = None  # type: ignore
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
            if timeindex == 0:
                p.hbar(y="y", left="left", right="right", height=0.75, fill_color="color", source=ColumnDataSource(data), legend_group="legend_label")
            else:
                p.hbar(y="y", left="left", right="right", height=0.75, fill_color="color", source=ColumnDataSource(data))
        return p

#TODO Nur invoices mit invStat paid sollten als Umsatz gezählt werden, mangels Daten in musterpraxis vorerst weggelassen -> where invStat = "paid";
#TODO combinedName ungünstiger Schlüssel bei gleichnamigen Dr... -> executingDoctor verwenden?
class TurnoverPerMonthFigure(BokehFigure):
    def setup_figure(self):
        turnover_by_executing_doctor = self.data["turnover_by_executing_doctor"].dataframe
        executing_doctors = turnover_by_executing_doctor["combinedName"].drop_duplicates().dropna()
        executing_doctors = list(executing_doctors)
        df_split_by_personnel = pd.DataFrame()
        df_split_by_personnel["date"] = turnover_by_executing_doctor["date"].drop_duplicates()
        for combinedName in executing_doctors:
            df_split_by_personnel[combinedName] = pd.merge(df_split_by_personnel, turnover_by_executing_doctor[turnover_by_executing_doctor["combinedName"] == combinedName], on="date", how="outer")["SumTotalAmount"].fillna(0)

        #dataframe formatting, sum daily sums by month, index by month, columns for doctors names, values are turnover
        monthly_turnover_summary = turnover_by_executing_doctor.groupby([turnover_by_executing_doctor.date.dt.to_period('M'),"combinedName"], as_index=True).sum().reset_index()
        monthly_turnover_summary = monthly_turnover_summary.pivot(index="date", columns="combinedName", values="SumTotalAmount").fillna(0)
        monthly_turnover_summary.index =  monthly_turnover_summary.index.start_time + pd.offsets.SemiMonthEnd() #ensure monthly vbar is centered in the month, not at the start
        

        hover = HoverTool(names=executing_doctors, tooltips=[('Datum', '@date{%F}'),("Name","$name"),("Umsatz","@$name SFr")], formatters={'@date': 'datetime'})
        p = figure(title="Umsatz pro Arzt",
                   y_axis_label="Umsatz in SFr",
                   x_axis_type="datetime",
                   tools=['pan', 'box_zoom', 'wheel_zoom', 'save','reset', hover])
        p.toolbar.logo = None  # type: ignore

        p.vbar_stack(executing_doctors,
                     x="date",
                     color=brewer['Spectral'][len(executing_doctors)],
                     fill_alpha=0.35,
                     width=64_000_000 * 30,
                     name=executing_doctors, 
                     line_width=1,
                     source=monthly_turnover_summary)

        p.varea_stack(executing_doctors,
                      x='date',
                      color=brewer['Spectral'][len(executing_doctors)],
                      legend_label=executing_doctors,
                      name=executing_doctors,
                      source=df_split_by_personnel)
        return p


class BenefitsByInvoiceStatusPerDayFigure(BokehFigure):
    def setup_figure(self):
        df = self.data["benefits_by_invoice_status"].dataframe
        benefits_by_invoice_status_per_day = df.groupby([df.date.dt.to_period('D'),"invStat"], as_index=True).sum().reset_index()
        benefits_by_invoice_status_per_day = benefits_by_invoice_status_per_day.pivot(index="date", columns="invStat", values="effCalcAmtVat").fillna(0)

        #dataframe formatting, sum daily sums by month, index by month, columns for invoice states, values are benefits
        monthly_benefits_by_invoice_status_summary = df.groupby([df.date.dt.to_period('M'),"invStat"], as_index=True).sum().reset_index()
        monthly_benefits_by_invoice_status_summary = monthly_benefits_by_invoice_status_summary.pivot(index="date", columns="invStat", values="effCalcAmtVat").fillna(0)
        monthly_benefits_by_invoice_status_summary.index =  monthly_benefits_by_invoice_status_summary.index.start_time + pd.offsets.SemiMonthEnd() 

        #we require at least 3 columns for bookehs color palettes to work
        for missing_required_column in {"open", "paid", "cancelled"}.difference(benefits_by_invoice_status_per_day.columns):
            benefits_by_invoice_status_per_day[missing_required_column] = 0.0
            monthly_benefits_by_invoice_status_summary[missing_required_column] = 0.0
        
        invoice_states_translation = {"open":"Offen",
                                      "paid":"Bezahlt",
                                      "cancelled": "Storniert",
                                      "reminder_1": "erste Mahnung",
                                      "reminder_2": "zweite Mahnung",
                                      "reminder_3": "dritte Mahnung",
                                      "reminder_last": "letzte Mahnung",
                                      "collection_active": "Inkasso",
                                      "booked_out": "Ausgebucht"}

        benefits_by_invoice_status_per_day.rename(columns=invoice_states_translation, inplace=True)
        monthly_benefits_by_invoice_status_summary.rename(columns=invoice_states_translation, inplace=True)

        invoice_states = [state for state in benefits_by_invoice_status_per_day.columns]


        hover = HoverTool(names=invoice_states, tooltips=[('Datum', '@date{%F}'),("Name","$name"),("Leistung","@$name SFr")], formatters={'@date': 'datetime'})
        p = figure(title="Leistungen nach Rechnungsstand",
            y_axis_label="Leistungen in SFr",
            x_axis_type="datetime",
            tools=['pan', 'box_zoom', 'wheel_zoom', 'save','reset', hover])
        p.toolbar.logo = None  # type: ignore

        p.vbar_stack(invoice_states,
                     x="date",
                     color=brewer['Spectral'][len(invoice_states)],
                     fill_alpha=0.35,
                     width=64_000_000 * 30,
                     name=invoice_states, 
                     line_width=1,
                     source=monthly_benefits_by_invoice_status_summary)

        p.varea_stack(invoice_states,
                      x="date",
                      color=brewer['Spectral'][len(invoice_states)],
                      legend_label=invoice_states,
                      name=invoice_states,
                      source=benefits_by_invoice_status_per_day)

        return p

class TurnoverByServiceTypeFigure(BokehFigure):
    def setup_figure(self):
        turnover_by_service_type_per_day = self.data["turnover_by_service_type_per_day"].dataframe
        
        service_types_translation = {"SumTotalTar":"Tarmed (Medizinisch)",
                                     "SumTotalTar2":"Tarmed (Technisch)",
                                     "SumTotalMedication": "Medikation",
                                     "SumTotalMigel": "Mittel und Gegenstände (MiGeL)",
                                     "SumTotalAnalysis": "Labor",
                                     "SumTotalPhysio": "Physio",
                                     "SumTotalMisc": "Verschiedenes",
                                     "SumTotalOther": "Sonstige Aufwände"}

        service_types = list(service_types_translation.values())

        turnover_by_service_type_per_day.rename(columns=service_types_translation, inplace=True)

        turnover_by_service_type_per_month =  turnover_by_service_type_per_day.groupby([turnover_by_service_type_per_day.date.dt.to_period('M')], as_index=True).sum().reset_index()
        turnover_by_service_type_per_month.date = turnover_by_service_type_per_month.date.astype('datetime64[ns]') + pd.offsets.SemiMonthEnd()

        hover = HoverTool(names=service_types, tooltips=[('Datum', '@date{%F}'),("Name","$name"),("Leistung","@$name{0.00} SFr")], formatters={'@date': 'datetime'})
        p = figure(title="Umsatz nach Leistungsart",
                   y_axis_label="Umsatz in SFr",
                   x_axis_type="datetime",
                   tools=['pan', 'box_zoom', 'wheel_zoom', 'save','reset', hover])
        p.toolbar.logo = None  # type: ignore

        p.vbar_stack(service_types,
                     x="date",
                     color=brewer['Spectral'][len(service_types)],
                     fill_alpha=1.00,
                     width=64_000_000,
                     name=service_types, 
                     line_width=0,
                     source=turnover_by_service_type_per_day)

        p.vbar_stack(service_types,
                     x="date",
                     color=brewer['Spectral'][len(service_types)],
                     fill_alpha=0.35,
                     width=64_000_000 * 30,
                     name=service_types, 
                     line_width=0.4,
                     legend_label=service_types,
                     source=turnover_by_service_type_per_month)

        return p
