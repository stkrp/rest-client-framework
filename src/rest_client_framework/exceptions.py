class RestFrameworkException(Exception):
    pass


class ModelException(RestFrameworkException):
    pass


class ModelInstanceIsNotUnique(ModelException):
    pass


class ModelInstanceNotExists(ModelException):
    pass
