import copy
from typing import Any, Iterator, Union, Dict, Generator
from itertools import islice

from requests import Request

from .exceptions import ModelInstanceIsNotUnique, ModelInstanceNotExists
from .executors import BaseExecutor, ExecutorRequired
from .models import BaseModel


class BaseRecordSet(ExecutorRequired):
    """ 
    Коллекция моделей
     
    "Ленивая", т. е. можно передавать по конвейеру для настройки, а запрос 
    к серверу будет выполнен только в самом конце.
    """
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
        # TODO: Продумать, нужно ли для `slice` отдавать новый `RecordSet`
        self._initiate_cache()
        return self._cache[item]

    def copy(self) -> 'BaseRecordSet':
        copy_ = self.__class__(
            self.path, self.model_class, executor=self.executor,
        )
        copy_._request = copy.deepcopy(self._request)
        return copy_

    def filter(self, params: Dict[str, Any]) -> 'BaseRecordSet':
        # Параметры передаются в виде словаря для того, чтобы поддерживать
        # поля, имена которых не допустимы в Python как имена идентификаторов.
        copy_ = self.copy()
        copy_._request.params.update(params)
        return copy_

    def get(self, params: Dict[str, Any]) -> BaseModel:
        """ 
        Возвращает единственный найденый экземпляр модели
        
        В любом другом случае возбуждает исключение
        """

        # Для неуникальности достаточно, чтобы существовало больше одного
        # объекта, поэтому при наличии двух результатов, возбуждаем исключение
        min_non_unique_length = 2
        candidates = tuple(
            islice(self.filter(params).iterator(), min_non_unique_length)
        )

        if len(candidates) == min_non_unique_length:
            raise ModelInstanceIsNotUnique(candidates)

        # Пустой результат тоже не допустим, поэтому возбуждаем исключение
        if not candidates:
            raise ModelInstanceNotExists(candidates)

        return candidates[0]

    def first(self) -> BaseModel:
        return next(self.copy().iterator(), None)

    def iterator(self) -> Generator[BaseModel, None, None]:
        response = self.executor(self._request)
        # TODO: Добавить проверку данных ответа (должен быть итерируемый объект)  # NoQA
        for item in response.parsed_data:
            yield self.model_class(executor=self.executor, **item)

    def _initiate_cache(self, force: bool = False) -> None:
        if self._cache is None or force:
            self._cache = list(self.iterator())

