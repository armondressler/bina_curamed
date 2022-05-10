from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.models.formatters import BasicTickFormatter, DatetimeTickFormatter


class BokehFigure:
    def __init__(self, data):
        self.data = data
        self.figure = self.setup_figure()

    def as_json(self):
        return json_item(self.figure)

    def setup_figure(self):
        pass


class AnzahlNeueFaelleProTag(BokehFigure):
    def setup_figure(self):
        p = figure(title="Neue Fälle pro Tag", y_axis_label="Neue Fälle", x_range=self.data.get("date"))
        p.vbar(x=self.data.get("date"), top=self.data.get("cases"), color="green", width=0.8)
        #p.line(x=self.data.get("date"), y=self.data.get("cases"), color="green")
        p.yaxis.minor_tick_out = 0
        show(p)

class DurchschnittAlterProSitzung(BokehFigure):
    def setup_figure(self):
        p = figure(title="Durchschnittsalter Patient pro Sitzung", y_axis_label="Durchschnittsalter", x_range=self.data.get("date"))