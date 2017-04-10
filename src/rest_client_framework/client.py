from .executor import BaseExecutor


class BaseRestClient(object):
    def __init__(self, *, executor: BaseExecutor) -> None:
        self.executor = executor
