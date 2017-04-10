from requests import Request, Response

from rest_client_framework.clients import BaseRestClient
from rest_client_framework.resources import (
    ListResourceDescriptor, BaseResourceDescriptor, BaseResource,
)
from rest_client_framework.models import BaseModel
from rest_client_framework.executors import BaseExecutor
from rest_client_framework.recordsets import BaseRecordSet
from rest_client_framework.parsers import JsonParser, BaseParser


class Comment(BaseModel):
    pass


class Post(BaseModel):
    comments = ListResourceDescriptor(
        '/posts/{instance.id}/comments/', Comment,
    )

    def __str__(self):
        return f'#{self.id} {self.title}'


class AuthResource(BaseResource):
    def login(self, username: str, password: str) -> Response:
        request = Request(
            'post',
            self._build_subpath('login'),
            data={'username': username, 'password': password},
        )
        response = self.executor(request)
        self.executor.auth_token = '!CusTom#Str1n6'
        return response


class DemoExecutor(BaseExecutor):
    def __init__(self, url: str, custom_header: str, *, parser: BaseParser):
        super().__init__(url, parser=parser)
        self.custom_header = custom_header
        self.auth_token = None

    def _setup_request(self, request: Request) -> None:
        super()._setup_request(request)
        request.headers['Custom-Header'] = self.custom_header
        if self.auth_token is not None:
            if request.cookies is None:
                request.cookies = {}
            request.cookies['auth-token'] = self.auth_token


class DemoRestClient(BaseRestClient):
    auth = BaseResourceDescriptor('/users/', resource_class=AuthResource)
    posts = ListResourceDescriptor('/posts/', Post, BaseRecordSet)


if __name__ == '__main__':
    api_client = DemoRestClient(
        executor=DemoExecutor(
            'https://jsonplaceholder.typicode.com/', 'MyCustomHeaderValue',
            parser=JsonParser(),
        )
    )
    posts = api_client.posts.select()
    print(*posts, sep='\n')
    print('-' * 80)
    print(*posts.filter(userId=5), sep='\n')
    print(api_client.auth.login('name', 'pass').json())
    # print(posts[0].params['id'])
    print(*posts[0].comments.select(), sep='\n')
