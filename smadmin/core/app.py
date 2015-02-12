from functools import wraps
import importlib
import logging

from google.appengine.ext.webapp import template
import webapp2


class AdminApplication(webapp2.WSGIApplication):
    '''
    The Application Admin is the central element in the admin framework.
    It keeps references and reverse references to AdminModel classes and ndb
    Model classes.
    And since it inherits from webapp2.WSGIApplication, it also natively
    directs HTTP requests to the right Request Handlers.
    '''

    def __init__(self, *args, **kwargs):
        '''
        AdminApplication initialization method. Initializes data structures
        that keep track of AdminModel classes and ndb Model classes.
        '''
        super(AdminApplication, self).__init__(*args, **kwargs)
        self.registered_models = {}
        self.models_by_partial_key_format = {}
        self.models_by_key_format = {}
        self.routes_prefix = ''

    def get_table_names(self):
        '''
        Use the AdminApplication internal data to return the list of ndb Model
        classes registered in the admin app.

        Returns:
            list: table names (list of strings).
        '''
        table_names = [k[0] for k in self.models_by_partial_key_format]
        table_names.sort()
        return table_names

    def register(self, model_admin, model):
        '''
        Bind a AdminModel class to an ndb Model class.
        The registration process has 2 steps:

        * Create internal references to bind the AdminModel and ndb.Model
          classes to be able to:

          * Find an ``AdminModel`` class using an ``ndb.Model`` name
          * Find an ndb.Model class using a partial ``KEY_FORMAT``
            (e.g.: ``('PropertyBase', int, 'UserSong')`` ->
            ``<class models.UserSong>``)
          * Find an ndb.Model class using a full ``KEY_FORMAT``
            (e.g.: ``('PropertyBase', int, 'UserSong', int)`` ->
            ``<class models.UserSong>``)
        * Generate the webapp2 Routes for each ``AdminModel``, and register
          them in the app.

        Args:
            model_admin: AdminModel class object.

            model: ndb.Model class object.

        Returns:
            None.
        '''
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
        Register the Home View Route.

        Returns:
            None.
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
        Import Python modules from the project that uses the admin.
        AdminModel classes that are decorated with ``register()`` will be
        registered in the AdminApplication.

        Args:
            modules: list of strings that represent importable Python modules.

        Returns:
            None.
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

'''
Test
'''
app = AdminApplication()  # plop
'''
Test 2
'''

# Register custom Template Filters
template.register_template_library('smadmin.core.smtemplatefilters')


class register(object):
    '''
    Class decorator to register an ndb Model with an AdminModel.
    '''
    def __init__(self, model):
        '''
        Initialize the ``register`` decorator to save the ``ndb.Model`` class.
        A ``AdminModel`` class will be bound to that ``ndb.Model`` class when
        the ``AdminApplication`` imports the module that contains the
        ``AdminModel`` class.
        '''
        self.model = model

    def __call__(self, cls):
        '''
        Method called when the decorated ``AdminModel`` class is imported.
        This allows the ``AdminApplication`` to bind the ``AdminModel`` to the
        ``ndb.Model``.
        '''
        app.register(cls, self.model)
        cls.model = self.model

        @wraps(cls)
        def wrapper(*args, **kwargs):
            pass
        return wrapper
