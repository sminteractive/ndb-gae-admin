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


def get_key_format_from_url_parameters(parameters):
    '''

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
    # We're dealing with a "table", which is represented by a partial key that
    # has an odd number of elements
    # (kind1)
    # (kind1, id1, kind2)
    # etc
    assert(len(parameters) % 2 == 1)
    _key_format = get_key_format_from_url_parameters(parameters)
    return admin.app.models_by_partial_key_format.get(_key_format)


def _from_url_parameters_to_ndb_flat_key(model, parameters):
    converted_parameters = []
    for i, item in enumerate(parameters):
        if i % 2 == 1:
            # We have to convert numerical IDs because they're extracted from
            # the URL path and parsed as strings.
            #
            # And we can't automatically parse URL path components that are
            # castable into integers since we may have ndb Keys like this:
            # ndb.Key('my_kind', '42')
            # which would be different than ndb.Key('my_kind', 42)
            if model.KEY_FORMAT[i] in (long, int):
                try:
                    item = int(item)
                except Exception:
                    pass
        converted_parameters.append(item)
    return converted_parameters


def get_entity_from_request_handler_parameters(parameters):
    # We're dealing with an "entity", which is represented by a full key that
    # has an even number of elements
    # (kind1, id1)
    # (kind1, id1, kind2, id2)
    # etc
    assert(len(parameters) % 2 == 0)
    _key_format = get_key_format_from_url_parameters(parameters)
    _model = admin.app.models_by_partial_key_format.get(_key_format[:-1])
    _flat_key = _from_url_parameters_to_ndb_flat_key(_model, parameters)
    _ndb_key = ndb.Key(flat=_flat_key)
    return _ndb_key.get()


def get_admin_model_from_model(model):
    return admin.app.registered_models.get(model.__name__)


class AdminModel(object):
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
