class BaseModel(object):
    def __init__(self, params, *, executor):
        self.params = params
        self.executor = executor

    def __str__(self):
        return str(self.params)

    def __repr__(self):
        return str(self.params)

    def save(self) -> 'BaseModel':
        return self
