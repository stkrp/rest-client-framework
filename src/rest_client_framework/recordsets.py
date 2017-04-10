import copy
from typing import Any, Iterator, Union, Dict, Generator

from requests import Request

from .executors import BaseExecutor, ExecutorRequired
from .models import BaseModel


class BaseRecordSet(ExecutorRequired):
    def __init__(
        self, path: str, model_class: type, *, executor: BaseExecutor
    ) -> None:
        super().__init__(executor=executor)
        self.path = path
        self.model_class = model_class

        # По умолчанию все запросы на получение
        self._request = Request(method='get', url=self.path)
        self._cache = None

    def __len__(self):
        self._initiate_cache()
        return len(self._cache)

    def __iter__(self) -> Iterator:
        self._initiate_cache()
        return iter(self._cache)

    def __getitem__(self, item: Union[int, slice]) -> BaseModel:
        self._initiate_cache()
        return self._cache[item]

    def copy(self) -> 'BaseRecordSet':
        copy_ = self.__class__(
            self.path, self.model_class, executor=self.executor,
        )
        copy_._request = copy.deepcopy(self._request)
        return copy_

    def filter(self, **kwargs: Dict[str, Any]) -> 'BaseRecordSet':
        copy_ = self.copy()
        copy_._request.params.update(**kwargs)
        return copy_

    def iterator(self) -> Generator[BaseModel, None, None]:
        response = self.executor(self._request)
        # TODO: Добавить проверку данных ответа (должен быть итерируемый объект)  # NoQA
        for item in response.parsed_data:
            yield self.model_class(executor=self.executor, **item)

    def _initiate_cache(self, force: bool = False) -> None:
        if self._cache is None or force:
            self._cache = list(self.iterator())

