import pandas as pd
import numpy as np
from pandas import Timestamp

a = {"date": {0: Timestamp('1900-01-01 08:03:00'), 1: Timestamp('1900-01-01 08:03:00'), 2: Timestamp('1900-01-01 11:03:00'), 3: Timestamp('1900-01-01 08:03:00'), 4: Timestamp('1900-01-01 13:03:00')},"age": {0: 1, 1: 1, 2: 1, 3: 1, 4: 65}}

from bokeh.plotting import figure, show
from bokeh.plotting import ColumnDataSource

source = ColumnDataSource(data={
    '0 - 10': [10, 4, 3, 0, 0],
    '10 - 12': [7, 7, 5, 2, 0],
    '12 - 15': [1, 4, 2, 2, 3],
    '15 - 24': [0, 0, 2, 4, 10]
})


from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, show

output_file("hbar_stack.html")

source = ColumnDataSource(data={
    "y": [1, 2, 3, 4, 5],
    "x1":[1, 2, 4, 3, 4],
    "x2": [1, 4, 2, 2, 3],
})
p = figure(width=400, height=400)

p.hbar_stack(['x1', 'x2'], y='y', height=0.8, color=("grey", "lightgrey"), source=source)

show(p)