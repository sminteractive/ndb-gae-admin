from functools import wraps
import importlib
import logging

from google.appengine.ext.webapp import template
import webapp2


class AdminApplication(webapp2.WSGIApplication):

    def __init__(self, *args, **kwargs):
        super(AdminApplication, self).__init__(*args, **kwargs)
        self.registered_models = {}
        self.models_by_partial_key_format = {}
        self.models_by_key_format = {}
        self.routes_prefix = ''

    def get_table_names(self):
        table_names = [k[0] for k in self.models_by_partial_key_format]
        table_names.sort()
        return table_names

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

    def _register_home_route(self):
        '''
        Register the Home route.
        This is subject to change depending on what we end up doing in the home
        page.
        '''
        self.router.add(
            webapp2.Route(
                r'{prefix}'.format(prefix=self.routes_prefix),
                handler='smadmin.core.request_handlers.HomeViewRequestHandler',
                name='smadmin-home-view',
                methods=['GET'],
                schemes=['http', 'https']
            )
        )

    def discover_admins(self, *modules):
        '''
        Modules that contain ModelAdmin classes need to be imported so we can
        register them.
        '''
        for module in modules:
            try:
                # TODO: handle packages and relative imports
                importlib.import_module(module)
            except Exception, e:
                logging.exception(e)
                pass
        # At this point, all Model Admins are suppose to be registered
        self._register_home_route()


# Enabled PATCH method
# http://stackoverflow.com/questions/16280496
allowed_methods = AdminApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
AdminApplication.allowed_methods = new_allowed_methods


app = AdminApplication()

# Register custom Template Filters
template.register_template_library('smadmin.core.smtemplatefilters')


class register(object):
    '''
    Class decorator to register an ndb Model with an AdminModel
    '''
    def __init__(self, model):
        self.model = model

    def __call__(self, cls):
        app.register(cls, self.model)
        cls.model = self.model

        @wraps(cls)
        def wrapper(*args, **kwargs):
            pass
        return wrapper
