from typing import Any

from requests import Response


class BaseParser(object):
    def __call__(self, response: Response) -> Any:
        raise NotImplementedError


class JsonParser(BaseParser):
    def __call__(self, response: Response) -> Any:
        return response.json()
