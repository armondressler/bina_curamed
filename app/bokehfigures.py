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
        p = figure(x_axis_type="datetime", title="Neue Fälle pro Tag", x_axis_label="", y_axis_label="Neue Fälle", x_range=self.data.get("date"))
        p.vbar(x=self.data.get("date"), top=self.data.get("cases"), color="green", width=0.8)
        #p.xaxis[0].formatter = DatetimeTickFormatter()
        p.yaxis.minor_tick_out = 0
        show(p)
