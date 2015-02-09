from functools import wraps
import importlib
import logging

import webapp2


class AdminApplication(webapp2.WSGIApplication):

    def __init__(self, *args, **kwargs):
        super(AdminApplication, self).__init__(*args, **kwargs)
        self.registered_models = {}
        self.models_by_partial_key_format = {}
        self.models_by_key_format = {}
        self.routes_prefix = ''

    def register(self, model_admin, model):
        logging.info('REGISTERING Admin Model {} with {}'.format(
            model_admin.__name__,
            model.__name__
        ))

        self.registered_models[model.__name__] = model_admin

        self.models_by_partial_key_format[model.KEY_FORMAT[-2:-1]] = model
        self.models_by_key_format[model.KEY_FORMAT] = model

        for route in model_admin.generate_routes(model):
            self.router.add(route)

    def discover_admins(self, *modules):
        '''
        Modules that contain ModelAdmin classes and that need to be imported so
        we can register them.
        '''
        for module in modules:
            try:
                # TODO: handle packages and relative imports
                importlib.import_module(module)
            except Exception, e:
                logging.exception(e)
                pass


# Enabled PATCH method
# http://stackoverflow.com/questions/16280496
allowed_methods = AdminApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
AdminApplication.allowed_methods = new_allowed_methods


app = AdminApplication()


class register(object):
    '''
    Class decorator to register an ndb Model(s) with an AdminModel
    '''
    def __init__(self, *models):
        self.models = models

    def __call__(self, cls):
        for model in self.models:
            logging.info('Register Decorator')
            app.register(cls, model)

        @wraps(cls)
        def wrapper(*args, **kwargs):
            pass
        return wrapper
