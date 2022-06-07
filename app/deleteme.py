import numpy as np
import pandas as pd
from pandas import Timestamp
from bokeh.palettes import Spectral6
from bokeh.plotting import ColumnDataSource, figure, show
from bokeh.models import HoverTool


a = {'date': {0: Timestamp('2021-11-24 00:00:00'), 1: Timestamp('2021-11-24 00:00:00'), 2: Timestamp('2022-02-20 00:00:00'), 3: Timestamp('2022-02-20 00:00:00'), 4: Timestamp('2022-02-20 00:00:00'), 5: Timestamp('2022-03-30 00:00:00')}, 'calcAmtTotal': {0: 66.65, 1: 7.3, 2: 333.2, 3: 83.0, 4: 94.15, 5: 85.9}, 'invStat': {0: 'paid', 1: 'paid', 2: 'open', 3: 'paid', 4: 'open', 5: 'paid'}}

df = pd.DataFrame.from_dict(a)
df["paid"] = df[df["invStat"] == "paid"]
df["open"] = df[df["invStat"] == "open"]

from bokeh.palettes import brewer
N=2
p = figure(x_range=(0, len(df)-1), y_range=(0, 800))
p.grid.minor_grid_line_color = '#eeeeee'

p.varea_stack(["paid","open"], x='date', color=("grey", "lightgrey"), source=df)
#show(p)