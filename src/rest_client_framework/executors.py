import copy
from typing import Any
from urllib.parse import urljoin

from requests import Request, Response, Session

from .parsers import BaseParser


class BaseExecutor(object):
    """ Исполнитель запросов """
    def __init__(self, url: str, *, parser: BaseParser) -> None:
        self.url = url
        self.parser = parser
        self.session = Session()

    def __call__(self, request: Request) -> Response:
        request = copy.deepcopy(request)
        self._setup_request(request)

        # Подготовка запроса выполняется без учета сессии специально,
        # чтобы изолировать запрос от других запросов
        # Если от изоляции нужно отказаться, то следует раскомментировать
        # код ниже, а имеющийся код удалить:
        # response = self.session.send(self.session.prepare_request(_request))
        response = self.session.send(request.prepare())
        self._setup_response(response)
        return response

    def _setup_request(self, request: Request) -> None:
        request.url = self._build_suburl(request.url)

    def _build_suburl(self, path: str) -> str:
        return urljoin(self.url, path)

    def _setup_response(self, response: Response) -> None:
        # FIXME: При `pickling` потеряется `parsed_data`
        # (можно отнаследовать `requests.Response` и расширить `__attrs__`)
        response.parsed_data = self._parse_response_data(response)

    def _parse_response_data(self, response: Response) -> Any:
        return self.parser(response)


class ExecutorRequired(object):
    def __init__(self, *, executor: BaseExecutor):
        self.executor = executor
