from requests import Request

from .executor import BaseExecutor


class BaseRecordSet(object):
    def __init__(
        self, path: str, model_class: type, *, executor: BaseExecutor
    ):
        self.path = path
        self.model_class = model_class
        self.executor = executor

        # По умолчанию все запросы на получение
        self._request = Request(method='get', url=self.path)

    def exec(self):
        return [
            self.model_class(raw_model, executor=self.executor)
            for raw_model in self.executor(self._request).json()
        ]
