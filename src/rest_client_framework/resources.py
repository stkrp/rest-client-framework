from typing import Union
from urllib.parse import urljoin

from .executors import BaseExecutor, ExecutorRequired
from .recordsets import BaseRecordSet


class BaseResource(ExecutorRequired):
    """ 
    Описывает End-point API и методы работы с ним.
    """
    def __init__(self, path: str, *, executor: BaseExecutor) -> None:
        super().__init__(executor=executor)
        self.path = path

    def _build_subpath(self, path_postfix: str) -> str:
        return urljoin(self.path, path_postfix)


class ListResource(BaseResource):
    record_set_class = BaseRecordSet

    def __init__(
        self, path: str, model_class: type, record_set_class: type = None,
        *, executor: BaseExecutor
    ) -> None:
        super().__init__(path, executor=executor)
        self.model_class = model_class

        if record_set_class is not None:
            self.record_set_class = record_set_class

    def select(self) -> record_set_class:
        return self.record_set_class(
            self.path, self.model_class, executor=self.executor,
        )


class BaseResourceDescriptor(object):
    """ 
    Фабрика ресурсов (`BaseResource`) для каждого экземпляра 
    произвольного класса, который содержит эту фабрику и `executor`
    """

    resource_class = BaseResource

    def __init__(
        self, path_template: str, *, resource_class: type = None
    ) -> None:
        self.path_template = path_template

        if resource_class is not None:
            self.resource_class = resource_class

    def __get__(
        self, instance: ExecutorRequired, owner: type,
    ) -> Union['BaseResourceDescriptor', resource_class]:
        if instance is None:
            return self
        # TODO: Можно сделать кэширование в `instance` для оптимизации
        return self._build_resource(instance)

    def _build_resource(self, instance: ExecutorRequired) -> resource_class:
        return self.resource_class(
            self._build_path(instance), executor=instance.executor,
        )

    def _build_path(self, instance: ExecutorRequired) -> str:
        return self.path_template.format(instance=instance)


class ListResourceDescriptor(BaseResourceDescriptor):
    resource_class = ListResource

    def __init__(
        self, path_template: str, model_class: type,
        record_set_class: type = None, *, resource_class: type = None
    ) -> None:
        super().__init__(path_template, resource_class=resource_class)
        self.model_class = model_class
        self.record_set_class = record_set_class

    def _build_resource(self, instance: ExecutorRequired) -> resource_class:
        return self.resource_class(
            self._build_path(instance),
            self.model_class,
            self.record_set_class,
            executor=instance.executor,
        )
