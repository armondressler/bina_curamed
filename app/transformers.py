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
    def __init__(self, date_column_name="date", gappable_column_name="cases", fill_gaps_with_value=0):
        self.date_column_name = date_column_name
        self.gappable_column_name = gappable_column_name
        self.fill_gaps_with_value = fill_gaps_with_value

    def transform(self, query_result: dict):
        from datetime import timedelta
        datecolumn = query_result.get(self.date_column_name)
        if datecolumn is None:
            raise QueryResultTransformationError(f"Column {self.date_column_name} missing in query result data (available: ???)")
        start_date = datecolumn[0]
        end_date = datecolumn[-1]

        delta = end_date - start_date
        if not isinstance(delta, timedelta):
            raise QueryResultTransformationError(f"Values in column {self.date_column_name} are not of type date ({type(start_date)})")

        gappable_column = query_result.get(self.gappable_column_name)
        if gappable_column is None:
            raise QueryResultTransformationError(f"Column {self.gappable_column_name} to be gapped with {self.fill_gaps_with_value} missing in query result data (available: ???)")

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            if day in datecolumn:
                continue
            datecolumn[i] = day
            gappable_column[i] = self.fill_gaps_with_value
        
        query_result[self.date_column_name] = datecolumn
        query_result[gappable_column] = gappable_column

        return query_result
