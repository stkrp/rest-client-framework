from urllib.parse import urljoin
from requests import request


class Executor(object):
    def __init__(self, root_path: str):
        self.root_path = root_path

    def __call__(self, method: str, path: str, *pargs, **kwargs):
        path = self._build_full_path(path)
        return request(method, path, *pargs, **kwargs)

    def _build_full_path(self, subpath: str) -> str:
        return urljoin(self.root_path, subpath)


class Model(object):
    def __init__(self, params, *, executor):
        self.params = params
        self.executor = executor

    def __str__(self):
        return str(self.params)

    def __repr__(self):
        return str(self.params)


class Resource(object):
    def __init__(self, subpath: str, model_class: type):
        self.subpath = subpath
        self.model_class = model_class

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return QuerySet(
            self.subpath.format(instance=instance),
            self.model_class,
            instance.executor,
        )


class QuerySet(object):
    def __init__(
        self, subpath: str, model_class: type, executor: Executor
    ):
        self.subpath = subpath
        self.query = {}
        self.model_class = model_class
        self.executor = executor

    def exec(self):
        return [
            self.model_class(raw_model, executor=self.executor)
            for raw_model in self.executor('get', self.subpath, params=self.query).json()
        ]


class Comment(Model):
    pass


class Post(Model):
    comments = Resource('/posts/{instance.params[id]}/comments', Comment)


class ApiClient(object):
    posts = Resource('/posts', Post)

    def __init__(self, root_path: str, auth_token: str):
        self.root_path = root_path
        self.auth_token = auth_token
        self.executor = Executor(root_path)


if __name__ == '__main__':
    api_client = ApiClient('https://jsonplaceholder.typicode.com', 'abc')
    posts = api_client.posts.exec()
    print(posts, sep='\n')
    print('-' * 80)
    # print(posts[0].params['id'])
    print(posts[0].comments.exec(), sep='\n')
