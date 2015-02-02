from functools import wraps

from admin import app


class register(object):
    '''
    Class decorator to register an ndb Model with an AdminModel
    '''
    def __init__(self, *model_admins):
        self.model_admins = model_admins

    def __call__(self, cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):
            for model_admin in self.model_admins:
                app.register(model_admin, cls)
        return wrapper
