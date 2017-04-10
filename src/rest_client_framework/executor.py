import copy
from urllib.parse import urljoin

from requests import Request, Response, Session


class BaseExecutor(object):
    def __init__(self, url: str):
        self.url = url
        self.session = Session()

    def __call__(self, request: Request) -> Response:
        request = copy.copy(request)
        self._setup_request(request)

        # Подготовка запроса выполняется без учета сессии специально,
        # чтобы изолировать запрос от других запросов
        # Если от изоляции нужно отказаться, то следует раскомментировать
        # код ниже, а имеющийся код удалить:
        # return self.session.send(self.session.prepare_request(_request))
        return self.session.send(request.prepare())

    def _setup_request(self, request: Request) -> None:
        request.url = self._build_suburl(request.url)

    def _build_suburl(self, path: str) -> str:
        return urljoin(self.url, path)
