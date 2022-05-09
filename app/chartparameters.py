from dataclasses import dataclass


@dataclass
class DBQuery:
    query: str
    params: tuple

class DBQueryTransformer:
    def __init__(self, queryresult: str, transformers: list):
        self.queryresult = queryresult
        self.transformers = transformers

    def transform(self):
        result = self.queryresult
        for transformer in self.transformers:
            result = transformer(result)
        return result

class BokehFigure:
    def __init__(self):
        pass


PARAMETERS = {
    "anzahl_neue_faelle": {}
}