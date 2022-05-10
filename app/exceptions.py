class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"Request failed to validate: {self.msg}"

class QueryResultTransformationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"Failed to transform query result: {self.msg}"