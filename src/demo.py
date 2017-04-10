from requests import Request, Response

from rest_client_framework.client import BaseRestClient
from rest_client_framework.resource import (
    ListResourceDescriptor, BaseResourceDescriptor, BaseResource,
)
from rest_client_framework.model import BaseModel
from rest_client_framework.executor import BaseExecutor
from rest_client_framework.recordset import BaseRecordSet


class Comment(BaseModel):
    pass


class Post(BaseModel):
    comments = ListResourceDescriptor(
        '/posts/{instance.params[id]}/comments/', Comment,
    )


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
    def __init__(self, url: str, custom_header: str):
        super().__init__(url)
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
        )
    )
    posts = api_client.posts.select().exec()
    print(posts, sep='\n')
    print('-' * 80)
    print(api_client.auth.login('name', 'pass').json())
    # print(posts[0].params['id'])
    print(posts[0].comments.select().exec(), sep='\n')
