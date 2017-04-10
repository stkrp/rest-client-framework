from .executors import BaseExecutor, ExecutorRequired


class BaseModel(ExecutorRequired):
    def __init__(self, *, executor: BaseExecutor, **params) -> None:
        super().__init__(executor=executor)
        # Для краткости используется простое отображение параметров в
        # поля объекта.
        # Это не будет работать, если у модели будет поле, имя которого
        # недопустимо в Python как имя идентификатора.
        for param_name, param_value in params.items():
            setattr(self, param_name, param_value)

    def save(self) -> 'BaseModel':
        # TODO: Определить сохранение через `executor`
        return self
