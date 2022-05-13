from typing import Dict
from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.models.formatters import BasicTickFormatter, DatetimeTickFormatter

from chartparameters import ConvertToHistogramTransformer, DBQuery, ConvertToDateTypeTransformer

from exceptions import ValidationError


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
        p = figure(title="Verteilung von Altersgruppen auf Sitzungszeiten", y_axis_label="Durchschnittsalter", x_range=df.get("time"))
        print(df.to_numpy())
        #p.quad(bottom=0, top=self.data[self.column_name], left=delays['left'], right=delays['right'], fill_color='red', line_color='black')


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