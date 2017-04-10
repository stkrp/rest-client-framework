from urllib.parse import urljoin
from requests import Request, Response, Session


class Executor(object):
    def __init__(self, root_url: str):
        self.root_url = root_url
        self.session = Session()

    def __call__(self, request: Request) -> Response:
        request.url = self._build_url(request.url)

        # Подготовка запроса выполняется без учета сессии специально,
        # чтобы изолировать запрос от других запросов
        # Если от изоляции нужно отказаться, то следует раскомментировать
        # код ниже, а имеющийся код удалить:
        # return self.session.send(self.session.prepare_request(_request))
        return self.session.send(request.prepare())

    def _build_url(self, path: str) -> str:
        return urljoin(self.root_url, path)


class Model(object):
    def __init__(self, params, *, executor):
        self.params = params
        self.executor = executor

    def __str__(self):
        return str(self.params)

    def __repr__(self):
        return str(self.params)


class ResourceDescriptor(object):
    def __init__(self, subpath: str, model_class: type):
        self.subpath = subpath
        self.model_class = model_class

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundResource(
            instance, self.subpath, instance.executor, self.model_class,
        )


class BoundResource(object):
    def __init__(self, owner, subpath, executor, model_class):
        self.owner = owner
        self.subpath = subpath
        self.executor = executor
        self.model_class = model_class

    def select(self):
        return RecordSet(
            self.subpath.format(instance=self.owner),
            self.model_class,
            self.executor,
        )


class RecordSet(object):
    def __init__(
        self, subpath: str, model_class: type, executor: Executor
    ):
        self.subpath = subpath
        self.request = Request(method='get', url=self.subpath)
        self.model_class = model_class
        self.executor = executor

    def exec(self):
        return [
            self.model_class(raw_model, executor=self.executor)
            for raw_model in self.executor(self.request).json()
        ]


class Comment(Model):
    pass


class Post(Model):
    comments = ResourceDescriptor('/posts/{instance.params[id]}/comments', Comment)


class ApiClient(object):
    posts = ResourceDescriptor('/posts', Post)

    def __init__(self, root_path: str, auth_token: str):
        self.root_path = root_path
        self.auth_token = auth_token
        self.executor = Executor(root_path)


if __name__ == '__main__':
    api_client = ApiClient('https://jsonplaceholder.typicode.com/', 'abc')
    posts = api_client.posts.select().exec()
    print(posts, sep='\n')
    print('-' * 80)
    # print(posts[0].params['id'])
    print(posts[0].comments.select().exec(), sep='\n')
