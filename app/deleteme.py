import numpy as np
import pandas as pd
from pandas import Timestamp
from bokeh.palettes import Spectral6
from bokeh.plotting import ColumnDataSource, figure, show
from bokeh.models import HoverTool
from numpy import nan


a = {'date': {0: Timestamp('2021-11-24 00:00:00'), 1: Timestamp('2021-11-24 00:00:00'), 2: Timestamp('2021-11-24 00:00:00'), 3: Timestamp('2021-11-24 00:00:00'), 4: Timestamp('2021-11-24 00:00:00'), 5: Timestamp('2021-11-25 00:00:00'), 6: Timestamp('2021-11-25 00:00:00'), 7: Timestamp('2021-11-25 00:00:00'), 8: Timestamp('2021-11-25 00:00:00'), 9: Timestamp('2021-11-25 00:00:00'), 10: Timestamp('2021-11-25 00:00:00'), 11: Timestamp('2021-11-25 00:00:00'), 12: Timestamp('2021-11-25 00:00:00'), 13: Timestamp('2021-11-25 00:00:00'), 14: Timestamp('2021-11-25 00:00:00'), 15: Timestamp('2021-11-26 00:00:00'), 16: Timestamp('2021-11-27 00:00:00'), 17: Timestamp('2021-11-28 00:00:00'), 18: Timestamp('2021-11-29 00:00:00'), 19: Timestamp('2021-11-30 00:00:00'), 20: Timestamp('2021-12-01 00:00:00'), 21: Timestamp('2021-12-02 00:00:00'), 22: Timestamp('2021-12-03 00:00:00'), 23: Timestamp('2021-12-04 00:00:00'), 24: Timestamp('2021-12-05 00:00:00'), 25: Timestamp('2021-12-06 00:00:00'), 26: Timestamp('2021-12-07 00:00:00'), 27: Timestamp('2021-12-08 00:00:00'), 28: Timestamp('2021-12-09 00:00:00'), 29: Timestamp('2021-12-10 00:00:00'), 30: Timestamp('2021-12-11 00:00:00'), 31: Timestamp('2021-12-12 00:00:00'), 32: Timestamp('2021-12-13 00:00:00'), 33: Timestamp('2021-12-14 00:00:00'), 34: Timestamp('2021-12-15 00:00:00'), 35: Timestamp('2021-12-16 00:00:00'), 36: Timestamp('2021-12-17 00:00:00'), 37: Timestamp('2021-12-18 00:00:00'), 38: Timestamp('2021-12-19 00:00:00'), 39: Timestamp('2021-12-20 00:00:00'), 40: Timestamp('2021-12-21 00:00:00'), 41: Timestamp('2021-12-22 00:00:00'), 42: Timestamp('2021-12-23 00:00:00'), 43: Timestamp('2021-12-24 00:00:00'), 44: Timestamp('2021-12-25 00:00:00'), 45: Timestamp('2021-12-26 00:00:00'), 46: Timestamp('2021-12-27 00:00:00'), 47: Timestamp('2021-12-28 00:00:00'), 48: Timestamp('2021-12-29 00:00:00'), 49: Timestamp('2021-12-30 00:00:00'), 50: Timestamp('2021-12-31 00:00:00'), 51: Timestamp('2022-01-01 00:00:00'), 52: Timestamp('2022-01-02 00:00:00'), 53: Timestamp('2022-01-03 00:00:00'), 54: Timestamp('2022-01-04 00:00:00'), 55: Timestamp('2022-01-05 00:00:00'), 56: Timestamp('2022-01-06 00:00:00'), 57: Timestamp('2022-01-07 00:00:00'), 58: Timestamp('2022-01-08 00:00:00'), 59: Timestamp('2022-01-09 00:00:00'), 60: Timestamp('2022-01-10 00:00:00'), 61: Timestamp('2022-01-11 00:00:00'), 62: Timestamp('2022-01-12 00:00:00'), 63: Timestamp('2022-01-13 00:00:00'), 64: Timestamp('2022-01-14 00:00:00'), 65: Timestamp('2022-01-15 00:00:00'), 66: Timestamp('2022-01-16 00:00:00'), 67: Timestamp('2022-01-17 00:00:00'), 68: Timestamp('2022-01-18 00:00:00'), 69: Timestamp('2022-01-19 00:00:00'), 70: Timestamp('2022-01-20 00:00:00'), 71: Timestamp('2022-01-21 00:00:00'), 72: Timestamp('2022-01-22 00:00:00'), 73: Timestamp('2022-01-23 00:00:00'), 74: Timestamp('2022-01-24 00:00:00'), 75: Timestamp('2022-01-25 00:00:00'), 76: Timestamp('2022-01-26 00:00:00'), 77: Timestamp('2022-01-27 00:00:00'), 78: Timestamp('2022-01-28 00:00:00'), 79: Timestamp('2022-01-29 00:00:00'), 80: Timestamp('2022-01-30 00:00:00'), 81: Timestamp('2022-01-31 00:00:00'), 82: Timestamp('2022-02-01 00:00:00'), 83: Timestamp('2022-02-02 00:00:00'), 84: Timestamp('2022-02-03 00:00:00'), 85: Timestamp('2022-02-04 00:00:00'), 86: Timestamp('2022-02-05 00:00:00'), 87: Timestamp('2022-02-06 00:00:00'), 88: Timestamp('2022-02-07 00:00:00'), 89: Timestamp('2022-02-08 00:00:00'), 90: Timestamp('2022-02-09 00:00:00'), 91: Timestamp('2022-02-10 00:00:00'), 92: Timestamp('2022-02-11 00:00:00'), 93: Timestamp('2022-02-12 00:00:00'), 94: Timestamp('2022-02-13 00:00:00'), 95: Timestamp('2022-02-14 00:00:00'), 96: Timestamp('2022-02-15 00:00:00'), 97: Timestamp('2022-02-16 00:00:00'), 98: Timestamp('2022-02-16 00:00:00'), 99: Timestamp('2022-02-16 00:00:00'), 100: Timestamp('2022-02-16 00:00:00'), 101: Timestamp('2022-02-16 00:00:00'), 102: Timestamp('2022-02-17 00:00:00'), 103: Timestamp('2022-02-18 00:00:00'), 104: Timestamp('2022-02-18 00:00:00'), 105: Timestamp('2022-02-18 00:00:00'), 106: Timestamp('2022-02-18 00:00:00'), 107: Timestamp('2022-02-18 00:00:00'), 108: Timestamp('2022-02-18 00:00:00'), 109: Timestamp('2022-02-18 00:00:00'), 110: Timestamp('2022-02-18 00:00:00'), 111: Timestamp('2022-02-18 00:00:00'), 112: Timestamp('2022-02-18 00:00:00'), 113: Timestamp('2022-02-19 00:00:00'), 114: Timestamp('2022-02-20 00:00:00'), 115: Timestamp('2022-02-21 00:00:00'), 116: Timestamp('2022-02-22 00:00:00'), 117: Timestamp('2022-02-22 00:00:00'), 118: Timestamp('2022-02-22 00:00:00'), 119: Timestamp('2022-02-22 00:00:00'), 120: Timestamp('2022-02-23 00:00:00'), 121: Timestamp('2022-02-24 00:00:00'), 122: Timestamp('2022-02-25 00:00:00'), 123: Timestamp('2022-02-26 00:00:00'), 124: Timestamp('2022-02-27 00:00:00'), 125: Timestamp('2022-02-28 00:00:00'), 126: Timestamp('2022-03-01 00:00:00'), 127: Timestamp('2022-03-02 00:00:00'), 128: Timestamp('2022-03-03 00:00:00'), 129: Timestamp('2022-03-04 00:00:00'), 130: Timestamp('2022-03-05 00:00:00'), 131: Timestamp('2022-03-06 00:00:00'), 132: Timestamp('2022-03-07 00:00:00'), 133: Timestamp('2022-03-08 00:00:00'), 134: Timestamp('2022-03-09 00:00:00'), 135: Timestamp('2022-03-10 00:00:00'), 136: Timestamp('2022-03-11 00:00:00'), 137: Timestamp('2022-03-12 00:00:00'), 138: Timestamp('2022-03-13 00:00:00'), 139: Timestamp('2022-03-14 00:00:00'), 140: Timestamp('2022-03-15 00:00:00'), 141: Timestamp('2022-03-16 00:00:00'), 142: Timestamp('2022-03-17 00:00:00'), 143: Timestamp('2022-03-18 00:00:00'), 144: Timestamp('2022-03-19 00:00:00'), 145: Timestamp('2022-03-20 00:00:00'), 146: Timestamp('2022-03-21 00:00:00'), 147: Timestamp('2022-03-22 00:00:00'), 148: Timestamp('2022-03-23 00:00:00'), 149: Timestamp('2022-03-23 00:00:00'), 150: Timestamp('2022-03-23 00:00:00'), 151: Timestamp('2022-03-23 00:00:00'), 152: Timestamp('2022-03-24 00:00:00'), 153: Timestamp('2022-03-25 00:00:00'), 154: Timestamp('2022-03-26 00:00:00'), 155: Timestamp('2022-03-27 00:00:00'), 156: Timestamp('2022-03-28 00:00:00'), 157: Timestamp('2022-03-29 00:00:00'), 158: Timestamp('2022-03-30 00:00:00'), 159: Timestamp('2022-03-30 00:00:00'), 160: Timestamp('2022-03-30 00:00:00'), 161: Timestamp('2022-03-30 00:00:00')}, 'effCalcAmtVat': {0: 11.27, 1: 8.01, 2: 16.0, 3: 16.0, 4: 15.35, 5: 7.3, 6: 11.27, 7: 8.01, 8: 16.0, 9: 16.0, 10: 7.2, 11: 8.01, 12: 16.0, 13: 16.0, 14: 7.2, 15: nan, 16: nan, 17: nan, 18: nan, 19: nan, 20: nan, 21: nan, 22: nan, 23: nan, 24: nan, 25: nan, 26: nan, 27: nan, 28: nan, 29: nan, 30: nan, 31: nan, 32: nan, 33: nan, 34: nan, 35: nan, 36: nan, 37: nan, 38: nan, 39: nan, 40: nan, 41: nan, 42: nan, 43: nan, 44: nan, 45: nan, 46: nan, 47: nan, 48: nan, 49: nan, 50: nan, 51: nan, 52: nan, 53: nan, 54: nan, 55: nan, 56: nan, 57: nan, 58: nan, 59: nan, 60: nan, 61: nan, 62: nan, 63: nan, 64: nan, 65: nan, 66: nan, 67: nan, 68: nan, 69: nan, 70: nan, 71: nan, 72: nan, 73: nan, 74: nan, 75: nan, 76: nan, 77: nan, 78: nan, 79: nan, 80: nan, 81: nan, 82: nan, 83: nan, 84: nan, 85: nan, 86: nan, 87: nan, 88: nan, 89: nan, 90: nan, 91: nan, 92: nan, 93: nan, 94: nan, 95: nan, 96: nan, 97: 8.01, 98: 16.0, 99: 16.0, 100: 5.95, 101: 65.1, 102: nan, 103: 8.01, 104: 16.0, 105: 16.0, 106: 8.01, 107: 16.0, 108: 16.0, 109: 5.95, 110: 65.1, 111: 5.95, 112: 65.1, 113: nan, 114: nan, 115: nan, 116: 43.0, 117: 8.01, 118: 16.0, 119: 16.0, 120: nan, 121: nan, 122: nan, 123: nan, 124: nan, 125: nan, 126: nan, 127: nan, 128: nan, 129: nan, 130: nan, 131: nan, 132: nan, 133: nan, 134: nan, 135: nan, 136: nan, 137: nan, 138: nan, 139: nan, 140: nan, 141: nan, 142: nan, 143: nan, 144: nan, 145: nan, 146: nan, 147: nan, 148: 52.760000000000005, 149: 8.29, 150: 16.56, 151: 16.56, 152: nan, 153: nan, 154: nan, 155: nan, 156: nan, 157: nan, 158: 44.5, 159: 8.29, 160: 16.56, 161: 16.56}, 'invStat': {0: 'open', 1: 'paid', 2: 'paid', 3: 'paid', 4: 'paid', 5: 'paid', 6: 'paid', 7: 'paid', 8: 'paid', 9: 'paid', 10: 'paid', 11: 'paid', 12: 'paid', 13: 'paid', 14: 'paid', 15: nan, 16: nan, 17: nan, 18: nan, 19: nan, 20: nan, 21: nan, 22: nan, 23: nan, 24: nan, 25: nan, 26: nan, 27: nan, 28: nan, 29: nan, 30: nan, 31: nan, 32: nan, 33: nan, 34: nan, 35: nan, 36: nan, 37: nan, 38: nan, 39: nan, 40: nan, 41: nan, 42: nan, 43: nan, 44: nan, 45: nan, 46: nan, 47: nan, 48: nan, 49: nan, 50: nan, 51: nan, 52: nan, 53: nan, 54: nan, 55: nan, 56: nan, 57: nan, 58: nan, 59: nan, 60: nan, 61: nan, 62: nan, 63: nan, 64: nan, 65: nan, 66: nan, 67: nan, 68: nan, 69: nan, 70: nan, 71: nan, 72: nan, 73: nan, 74: nan, 75: nan, 76: nan, 77: nan, 78: nan, 79: nan, 80: nan, 81: nan, 82: nan, 83: nan, 84: nan, 85: nan, 86: nan, 87: nan, 88: nan, 89: nan, 90: nan, 91: nan, 92: nan, 93: nan, 94: nan, 95: nan, 96: nan, 97: 'open', 98: 'open', 99: 'open', 100: 'open', 101: 'open', 102: nan, 103: 'open', 104: 'open', 105: 'open', 106: 'open', 107: 'open', 108: 'open', 109: 'open', 110: 'open', 111: 'open', 112: 'open', 113: nan, 114: nan, 115: nan, 116: 'paid', 117: 'paid', 118: 'paid', 119: 'paid', 120: nan, 121: nan, 122: nan, 123: nan, 124: nan, 125: nan, 126: nan, 127: nan, 128: nan, 129: nan, 130: nan, 131: nan, 132: nan, 133: nan, 134: nan, 135: nan, 136: nan, 137: nan, 138: nan, 139: nan, 140: nan, 141: nan, 142: nan, 143: nan, 144: nan, 145: nan, 146: nan, 147: nan, 148: 'open', 149: 'open', 150: 'open', 151: 'open', 152: nan, 153: nan, 154: nan, 155: nan, 156: nan, 157: nan, 158: 'paid', 159: 'paid', 160: 'paid', 161: 'paid'}}


df = pd.DataFrame.from_dict(a)

df["effCalcAmtVat"] = df["effCalcAmtVat"].fillna(0)
df["invStat"] = df["invStat"].fillna("paid")
df = df.groupby(["date","invStat"], as_index=True).sum().reset_index()
df = df.pivot(index="date", columns="invStat", values="effCalcAmtVat").fillna(0)
df["cancelled"] = 0.0
req = {"open", "paid", "cancelled"}

df.rename(columns = {'cancelled':'storniert', 'old_col2':'new_col2'}, inplace = True)

exit()

#b = {'date': {0: Timestamp('2021-09-20 00:00:00'), 1: Timestamp('2021-09-21 00:00:00'), 2: Timestamp('2021-09-22 00:00:00'), 3: Timestamp('2021-09-23 00:00:00'), 4: Timestamp('2021-09-24 00:00:00'), 5: Timestamp('2021-09-25 00:00:00'), 6: Timestamp('2021-09-26 00:00:00')}}
#df2 = pd.DataFrame.from_dict(b)
df2 = pd.DataFrame()
df2["date"] = pd.date_range("2021-09-20 00:00:00", "2021-09-26 00:00:00")


print(pd.merge(df2, df, on="date", how="left" ))

#print(pd.merge(df_split_by_personnel, df[df["combinedName"] == "Rudolf Rudelmann"], on="date", how="outer")["totalAmount"].fillna(0))


"""
for combinedName in df.combinedName.drop_duplicates():
    df_split_by_personnel[combinedName] = pd.merge(df_split_by_personnel, df[df["combinedName"] == combinedName], on="date", how="outer")["totalAmount"].fillna(0)

print(df_split_by_personnel)
p = figure(x_axis_type="datetime")
p.varea_stack([c for c in df.combinedName.drop_duplicates()], x='date', color=("grey", "lightgrey"), source=df_split_by_personnel)

show(p)"""



