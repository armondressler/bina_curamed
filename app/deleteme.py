import numpy as np
import pandas as pd
from pandas import Timestamp
from bokeh.palettes import Spectral6
from bokeh.plotting import ColumnDataSource, figure, show
from bokeh.models import HoverTool


from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

ds = ColumnDataSource(data=dict(
    x=[1,2,3,4,5],
    y=[1,3,2,4,3],
    y2=[3,5,4,6,5],
    desc=['A','b','C','d','E'],
))

p = figure(width=400, height=400, tooltips=[('index', '@y2')], title="Data xTreme")

p.varea('x','y','y2',source=ds)

show(p)


