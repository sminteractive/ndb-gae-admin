import webapp2
from google.appengine.ext import ndb

import smadmin as admin
from . import html
from .errors import AbstractClassError
from .errors import InvalidModelKeyFormatError
from .errors import NoModelKeyFormatError
from . import adminsearch


def get_url_path_components_from_ndb_model(model):
    '''
    A ``KEY_FORMAT`` can look like this:

    ``('User', (int, long))``

    ``('YouTubeUserInfo', basestring)``

    A ``KEY_FORMAT`` can also represent an ``ndb.Model`` entity with
    ancestor(s):

    ``('property_base', (basestring), 'user_song', (int, long))``

    This function takes that ``KEY_FORMAT`` and returns a list of components
    that can be used to create a webapp2 Route.

    Args:
        model:
            ``ndb.Model`` class that defines a ``KEY_FORMAT`` attribute, which
            is an iterable that represents a flat ndb Key.
            For example: ``('YouTubeUserInfo', basestring)``

    Returns:
        path_components:
            ``('(YouTubeUserInfo)', '(\d+)')``
    '''
    # The ndb model used in the admin must have a KEY_FORMAT attribute
    if getattr(model, 'KEY_FORMAT', None) is None:
        raise NoModelKeyFormatError(model)
    # An ndb.Key always has an even number items (kind1, id1, ...)
    if len(model.KEY_FORMAT) % 2 != 0:
        raise InvalidModelKeyFormatError()
    path_components = []
    for i, key_component in enumerate(model.KEY_FORMAT):
        # ndb.Key "kind" part
        if i % 2 == 0:
            path_components.append(r'<:({})>'.format(key_component))
        # ndb.Key "ID/name" part
        else:
            if key_component in (int, long):
                path_components.append(r'<:(\d+)>')
            else:
                path_components.append(r'<:(\s+)>')
    return path_components


def get_key_format_from_request_handler_parameters(parameters):
    '''
    Convert a list of ndb.Key items into a ``KEY_FORMAT``-like tuple.

    Here are a few examples:

    * ``('User',)`` -> ``('User',)``
    * ``('User', 42)`` -> ``('User', int)``
    * ``('PropertyBase', '1-sm-42', 'UserSong', 5312321)`` ->
      ``('PropertyBase', basestring, 'UserSong', int)``

    This function comes handy in the List View and Detail View Request Handlers
    when webapp2 passes a list of ``key_items`` parsed from the URL path.

    Args:
        parameters:
            List of items that represent an ndb flat Key (``('User', 42)``) or
            partial flat Key (``('User',)``).

    Returns:
        A ``KEY_FORMAT``-like tuple.
    '''
    converted_parameters = []
    for i, parameter in enumerate(parameters):
        # ID/name part of the component
        if i % 2 == 1:
            try:
                int(parameter)
                parameter = int
            except Exception:
                parameter = basestring
        converted_parameters.append(parameter)
    return tuple(converted_parameters)


def get_model_from_request_handler_parameters(parameters):
    '''
    The List View Request Handler needs to convert the parsed URL parameters
    into an ndb.Model class so we can list all its entities.

    For example:

    * ``('User',)`` -> ``<class models.User>``
    * ``('PropertyBase', '1-sm-42', 'UserSong', 12)``
        -> ``<class models.UserSong>``

    Args:
        parameters:
            List of items that represent a partial flat Key (``('User',)``).

    Returns:
        ``<class ndb.Model>`` class object.
    '''
    assert(len(parameters) % 2 == 1)
    _key_format = get_key_format_from_request_handler_parameters(parameters)
    return admin.app.models_by_partial_key_format.get(_key_format)


def get_entity_from_request_handler_parameters(parameters):
    '''
    The Detail View Request Handler needs to convert the parsed URL parameters
    into an ndb.Model instance so we can display and edit its properties.

    For example:

    * ``('User', 42)`` -> Entity that has the ``ndb.Key('User', 42)`` key.
    * ``('PropertyBase', '1-sm-42', 'UserSong', 12)``
        -> Entity that has the
        ``ndb.Key('PropertyBase', '1-sm-42', 'UserSong', 12)`` key.

    Args:
        parameters:
            List of items that represent a flat Key (``('User', 42)``).

    Returns:
        ndb Entity.
    '''
    assert(len(parameters) % 2 == 0)
    _key_format = get_key_format_from_request_handler_parameters(parameters)
    _model = admin.app.models_by_partial_key_format.get(_key_format[:-1])
    _flat_key = []

    for i, item in enumerate(parameters):
        if i % 2 == 1:
            # We have to convert numerical IDs because they're extracted from
            # the URL path and parsed as strings.
            #
            # And we can't automatically parse URL path components that are
            # castable into integers since we may have ndb Keys like this:
            # ndb.Key('my_kind', '42')
            # which would be different than ndb.Key('my_kind', 42)
            if _model.KEY_FORMAT[i] in (long, int):
                try:
                    item = int(item)
                except Exception:
                    pass
        _flat_key.append(item)

    _ndb_key = ndb.Key(flat=_flat_key)
    return _ndb_key.get()


def get_admin_model_from_model(model):
    '''
    Shorthand to map an ``ndb.Model`` class to the ``AdminModel`` class that
    registered it.

    Args:
        model:
            ``ndb.Model`` class.

    Returns:
        ``AdminModel`` class.
    '''
    return admin.app.registered_models.get(model.__name__)


class AdminModel(object):
    '''
    The AdminModel is the central element in the admin to display and
    manipulate ndb Models.

    It is responsible for a few things:
    * Register webapp2 Routes when the app launches for the first time
    * List entities and control their appearance
    * Register the search modules that can be used in the List View
    * Register the bulk actions that can used in the List View

    An important fact about the ``AdminModel`` class is that it will never get
    instatiated.

    That design can be explained by 2 things:
    * An ``AdminModel`` class will only be bound once to an ndb.Model, so the
      concept of _instance_ does not really apply in this case.
    * Even if we could instantiate ``AdminModel`` classes every time we need to
      to render the List and Detail View, directly defining class attributes
      makes the code more readable and compact.

    To define an ``AdminModel``, you can simply do this:

    ::

        MyAdmin(admin,AdminModel):
            pass

    The next step will be to bind an ``ndb.Model`` class to this admin:

    ::

        @admin.register(MyNdbModel)
        MyAdmin(admin.AdminModel):
            pass

    At this point, you can start using the admin with the default settings.
    '''
    model = None  # Populated when bound to a model
    fields = ()
    filters = ()
    actions = ()

    # List of properties to display in the list view.
    # When the list is empty, the view displays all the properties
    list_display = ()
    # Properties that should have a link to the entity view (detail view).
    list_display_links = ('key',)

    # List of properties to display in the detail view.
    # When the list is empty, the view displays all the properties
    detail_display = ()
    # Properties that can't be edited
    # Note that not matter what a user configures in a AdminModel subclass
    # the entity.key property will always be readonly
    detail_readonly = ()

    # Enable the default search
    default_search_enabled = True

    # The Admin may use multiple search methods.
    # By default, search() will be used, but in case a search needs pagination,
    # the Admin will have to define search modes that will be used to identify
    # a specific query (because we can't run 2 paginated queries at the same
    # time because of the cursor management).
    #
    # SEARCH_MODE_DEFAULT = 'default'
    # SEARCH_MODE_FIRST_NAME = 'first_name'
    # SEARCH_MODE_LAST_NAME = 'last_name'
    # search_modes = [
    #     {SEARCH_MODE_DEFAULT: 'by ID or email'},  # key qry + qry w/o cursor
    #     {SEARCH_MODE_FIRST_NAME: 'by First Name'},  # query with cursor
    #     {SEARCH_MODE_LAST_NAME: 'by Last Name'},  # query with cursor
    # ]
    #
    # def search(cls, search_string, cursor, mode=None):
    #     '''
    #     Search entities for the current ndb Model.
    #
    #     Args:
    #         search_string: string, strng to use to query entities.
    #
    #         cursor: ndb.Cursor, used to paginate the results.
    #
    #         mode: string (optional), the search method will receive a mode
    #               parameter if the "search_modes" list defines one or more
    #               search mode. The string passed will be one of the
    #               "search_modes" dicts keys.
    #
    #     Returns:
    #         (entities, next_cursor, more)
    #     '''
    #     if mode == SEARCH_MODE_DEFAULT:
    #         ...
    #     elif mode == SEARCH_MODE_FIRST_NAME:
    #         ...
    #     elif mode == SEARCH_MODE_LAST_NAME:
    #         ...
    #     else:
    #         return [], None, False  # (entities, next_cursor, more)
    #     return entities, next_cursor, more
    list_searches = []

    def __init__(self, *args, **kwargs):
        if self.__class__ == AdminModel:
            raise AbstractClassError(self.__class__)

    @classmethod
    def generate_routes(cls, model):
        '''
        Generate a list of webapp2 Routes based on the current ``AdminModel``
        configuration.

        Arguments:
            model:
                ``ndb.Model`` class object.

        Returned Values:
            list of webapp2 Routes.
        '''
        routes = []
        _path_components = get_url_path_components_from_ndb_model(model)
        # Add the route for the list view
        routes.append(
            webapp2.Route(
                r'{prefix}/{path}'.format(
                    prefix=admin.app.routes_prefix,
                    # Only get the last kind in the path component:
                    # (... , 'kind_n', id_n) -> 'kind_n'
                    # so we can access it at
                    # GET /admin/kind_n
                    path=r'/'.join(_path_components[-2:-1])
                ),
                handler='smadmin.core.request_handlers.ListViewRequestHandler',
                name='admin-list-view',
                methods=['GET'],
                schemes=['http', 'https']
            )
        )
        # Add the route for the detail view
        routes.append(
            webapp2.Route(
                r'{prefix}/{path}'.format(
                    prefix=admin.app.routes_prefix,
                    # Only get the last kind in the path component:
                    # (... , 'kind_n', id_n) -> 'kind_n'
                    # so we can access it at
                    # GET /admin/kind_n
                    path=r'/'.join(_path_components)
                ),
                handler='smadmin.core.request_handlers.DetailViewRequestHandler',
                name='admin-detail-view',
                methods=['GET'],
                schemes=['http', 'https']
            )
        )
        return routes

    @classmethod
    def generate_entity_form(cls, entity):
        '''
        '''
        entity_form = html.EntityForm(cls, entity)
        return entity_form

    @classmethod
    def get_available_search_by_name(cls, name):
        '''
        Inspect the ``AdminModel`` class and return a ListViewSearch class that
        matches the given name, if that ListViewSearch is in cls.list_searches.

        Args:
            name:
                string, name of the ``ListViewSearch`` class that is returned
                if it's present in ``cls.list_searches``.

        Returns:
            ListViewSearch class:
                None if the class is not in ``cls.list_searches``.
        '''
        assert(name)
        for list_view_search_class in cls.list_searches:
            if list_view_search_class.name == name:
                return list_view_search_class
        if cls.default_search_enabled \
                and adminsearch.DefaultListViewSearch.name == name:
            return adminsearch.DefaultListViewSearch
        return None
