"""
Демонстрационный модуль

Весь код представленный ниже качественно соответствует прототипу.
"""

from requests import Request, Response

from rest_client_framework.clients import BaseRestClient
from rest_client_framework.resources import (
    ListResourceDescriptor, BaseResourceDescriptor, BaseResource,
)
from rest_client_framework.models import BaseModel
from rest_client_framework.executors import BaseExecutor
from rest_client_framework.recordsets import BaseRecordSet
from rest_client_framework.parsers import JsonParser, BaseParser


# ---- Models --------------------------------------------------------------- #

class Comment(BaseModel):
    def __str__(self):
        return f'#{self.id} {self.name} (post: {self.postId})'


class Post(BaseModel):
    comments = ListResourceDescriptor(
        '/posts/{instance.id}/comments/', Comment,
    )

    def __str__(self):
        return f'#{self.id} {self.title} (user: {self.userId})'


class Todo(BaseModel):
    def __str__(self):
        return (
            f'#{self.id} {self.title} '
            f'(user: {self.userId}, completed: {self.completed})'
        )


class User(BaseModel):
    posts = ListResourceDescriptor('/users/{instance.id}/posts/', Post)
    todos = ListResourceDescriptor('/users/{instance.id}/todos/', Todo)

    def __str__(self):
        return f'#{self.id} {self.name}'


# ---- Resources ------------------------------------------------------------ #

class AuthResource(BaseResource):
    """ 
    Демонстрационный ресурс, показывающий, как можно расширить `executor` 
    
    На самом делеле API не поддерживает авторизацию, поэтому это всего лишь 
    эмуляция.
    """
    def login(self, username: str, password: str) -> Response:
        request = Request(
            'post',
            self._build_subpath('login'),
            data={'username': username, 'password': password},
        )
        response = self.executor(request)
        # При реальной авторизации токен должен был прийти от сервера
        # в `response`
        self.executor.auth_token = '!CusTom#Str1n6'
        return response


# ---- Executors ------------------------------------------------------------ #

class DemoExecutor(BaseExecutor):
    """
    Демонстрационный `executor`, показывающий, как можно расширить 
    базовый класс, например, для передачи собственных заголовков
    
    На самом деле API игнорирует эти заголовки
    """
    def __init__(self, url: str, custom_header: str, *, parser: BaseParser):
        super().__init__(url, parser=parser)
        self.custom_header = custom_header
        self.auth_token = None

    def _setup_request(self, request: Request) -> None:
        """
        Устанавливаем произвольный заголовок и, при наличии, токен авторизации
        """
        super()._setup_request(request)
        request.headers['Custom-Header'] = self.custom_header
        if self.auth_token is not None:
            if request.cookies is None:
                request.cookies = {}
            request.cookies['auth-token'] = self.auth_token

        # Информация для отладки
        authenticated_status_msg = (
            ('not ' if self.auth_token is None else '') + 'authenticated'
        )
        print(f'@ {authenticated_status_msg} request to {request.url}')


# ---- Rest clients --------------------------------------------------------- #

class DemoRestClient(BaseRestClient):
    auth = BaseResourceDescriptor('/auth/', resource_class=AuthResource)
    posts = ListResourceDescriptor('/posts/', Post)
    comments = ListResourceDescriptor('/comments/', Comment)
    todos = ListResourceDescriptor('/todos/', Todo)
    users = ListResourceDescriptor('/users/', User)


# ---- Utils ---------------------------------------------------------------- #

def print_record_set(record_set: BaseRecordSet, title=None):
    if not title:
        title = str(record_set)
    separator = '-' * 80

    print(separator)
    print(f'=> {title} start')
    print(*record_set, sep='\n')
    print(f'=> {title} end')
    print(separator)


if __name__ == '__main__':
    api_client = DemoRestClient(
        executor=DemoExecutor(
            'https://jsonplaceholder.typicode.com/', 'MyCustomHeaderValue',
            parser=JsonParser(),
        )
    )

    todos = api_client.todos.select()
    # API не умеет работать с явными True и False, поэтому используем строки
    # (только в демо-версии)
    uncompleted_todos = todos.filter({'completed': 'false'})

    print(todos.get({'id': 5}))
    print(uncompleted_todos.first())

    print_record_set(
        api_client.users.select().filter({'address.street': 'Dayna Park'}),
        'Users from Dayna Park street',
    )
    print_record_set(todos, 'All todos')
    print_record_set(uncompleted_todos, 'Uncompleted todos')

    # Аутентификация производится немного позже начала, чтобы
    # продемонстрировать неаутентифицированные запросы
    api_client.auth.login('login', 'password')

    non_existent_user = (
        api_client.users
        .select()
        .filter({'name': 'Non-existent user name'})
        .first()
    )
    print(non_existent_user)

    first_user = api_client.users.select().first()
    print(first_user)
    print_record_set(first_user.posts.select(), f'{first_user} posts')
    print_record_set(first_user.todos.select(), f'{first_user} todos')

    post_23 = api_client.posts.select().get({'id': 23})
    print(post_23)
    print_record_set(post_23.comments.select(), f'{post_23} comments')
