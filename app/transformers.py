import logging

import numpy as np
import pandas as pd

from exceptions import QueryResultTransformationError

log = logging.getLogger()

class DBQueryResultsTransformer:
    def transform(self, query_result):
        log.warning(f"Missing transform method for {type(self)}")
        raise QueryResultTransformationError(f"Missing transform method for {type(self)}")

class ConvertToDateTypeTransformer(DBQueryResultsTransformer):
    def __init__(self, date_format="%Y-%m-%d", date_column_name="date"):
        self.date_format = date_format
        self.date_column_name = date_column_name

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name], format=self.date_format)
        return dataframe

class RoundFloatTypeTransformer(DBQueryResultsTransformer):
    def __init__(self, float_column_name, digit_count=2) -> None:
        self.float_column_name=float_column_name
        self.digit_count = digit_count
    
    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        print(dataframe[self.float_column_name].max())
        dataframe[self.float_column_name] = dataframe[self.float_column_name].round(decimals=self.digit_count)
        print(dataframe[self.float_column_name].max())
        return dataframe        

class ConvertToHistogramTransformer(DBQueryResultsTransformer):
    """Return distribution of pandas column column_name into bins with a new dataframe with columns count, left, right"""
    def __init__(self, column_name, bins):
        self.column_name = column_name
        self.bins = bins

    def transform(self, dataframe) -> pd.DataFrame:
        values, bins = np.histogram(dataframe.get(self.column_name), bins=self.bins)
        return pd.DataFrame({"count": values, "left": [b for b in bins[:-1]], "right": [b for b in bins[1:]]})

class FillDateGapsTransformer(DBQueryResultsTransformer):
    def __init__(self, date_column_name="date", nan_fill={}):
        """Creates a new dataframe (calendar, 1 row per day) and performs a left join with the existing dataframe
           Gaps will result in NaN values in the new dataframe. These NaN values can be filled using nan_fill. nan_fill
           is a mapping of column_name to NaN replacement value.

        Args:
            date_column_name (str, optional): Name of the column containing the dates in the existing dataframe. Defaults to "date".
            nan_fill (dict, optional): Maps column names to NaN replacement values, e.g. {"TurnoverTotal": 0.0, "PetName": ""}. Defaults to {}.
        """
        self.date_column_name = date_column_name
        self.nan_fill = nan_fill

    def transform(self, dataframe: pd.DataFrame):
        datecolumn = dataframe.get(self.date_column_name)
        if datecolumn is None:
            raise QueryResultTransformationError(f"Column {self.date_column_name} missing in query result data (available: sel)")
        if dataframe[self.date_column_name].dtype != np.dtype('datetime64[ns]'):
            raise QueryResultTransformationError(f"Column {self.date_column_name} datatype is not np.datetime64 ({dataframe[self.date_column_name].dtype})")
        start_date = datecolumn.min()  # type: ignore
        end_date = datecolumn.max()  # type: ignore
        calendar_df = pd.DataFrame()
        calendar_df[self.date_column_name] = pd.date_range(start_date, end_date)
        calendar_df = pd.merge(calendar_df, dataframe, on=self.date_column_name, how="left")

        for column_name, nan_replacement in self.nan_fill.items():
            calendar_df[column_name].fillna(nan_replacement, inplace=True)
        
        return calendar_df
