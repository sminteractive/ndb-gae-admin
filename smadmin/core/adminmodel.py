import webapp2

import smadmin
from .errors import AbstractClassError
from .errors import InvalidModelKeyFormatError
from .errors import NoModelKeyFormatError


def get_url_path_components_from_ndb_model(model):
    '''
    A key format can look like this:
    ('User', (int, long))
    ('YouTubeUserInfo', basestring)

    Or represent an ndb Model with ancestor(s):
    ('property_base', (basestring), 'user_song', (int, long))

    This function takes that KEY_FORMAT and returns a list of components that
    can be used to create a webapp2 Route.

    Arguments:
        model: ndb.Model class that defines a KEY_FORMAT atribute, which is an
               iterable that represents a flat ndb Key. For example:
               ('YouTubeUserInfo', basestring)

    Returned Values:
        path_components: ('(YouTubeUserInfo)', '(\d+)')
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


def _convert_request_handler_parameters(parameters):
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


def get_entity_from_request_handler_parameters(parameters):
    # We're dealing with a "table", which is represented by a partial key that
    # ann odd number of elements
    # (kind1, id1)
    # (kind1, id1, kind2, id2)
    # etc
    assert(len(parameters) % 2 == 0)
    _key_format = _convert_request_handler_parameters(parameters)
    return smadmin.app.models_by_partial_key_format.get(_key_format)


def get_model_from_request_handler_parameters(parameters):
    # We're dealing with a "table", which is represented by a partial key that
    # ann odd number of elements
    # (kind1)
    # (kind1, id1, kind2)
    # etc
    assert(len(parameters) % 2 == 1)
    _key_format = _convert_request_handler_parameters(parameters)
    return smadmin.app.models_by_partial_key_format.get(_key_format)


def get_admin_model_from_model(model):
    return smadmin.app.registered_models.get(model.__name__)


class ModelAdmin(object):
    model = None  # Will be populated when bound to a model
    fields = ()
    filters = ()
    actions = ()

    # List of properties to display in the list view.
    # When the list is empty, the view displays all the properties
    list_display = ()
    # Properties that should have a link to the entity view (detail view).
    list_display_links = ('key',)

    # Message to display in the search input
    search_description = 'Search...'

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
    search_modes = []

    # "search" can be defined in a sublass as an instance method.
    # That method must conform to this signature and reponse
    # def search(self, search_string):
    #     # Query entities
    #     return entities, next_cursor, more
    search = None

    def __init__(self, *args, **kwargs):
        if self.__class__ == ModelAdmin:
            raise AbstractClassError(self.__class__)
        self.model = kwargs.get('model')
        assert(self.model)

    @classmethod
    def generate_routes(cls, model):
        '''
        Generate a list of webapp2 Routes based on the current Model Admin
        configuration.

        Arguments:
            model: ndb.Model class object.

        Returned Values:
            routes: list of webapp2 Routes.
        '''
        routes = []
        _path_components = get_url_path_components_from_ndb_model(model)
        # Add the route for the list view
        routes.append(
            webapp2.Route(
                r'{prefix}/{path}'.format(
                    prefix=smadmin.app.routes_prefix,
                    # Only get the last kind in the path component:
                    # (... , 'kind_n', id_n) -> 'kind_n'
                    # so we can access it at
                    # GET /admin/kind_n
                    path=r'/'.join(_path_components[-2:-1])
                ),
                handler='smadmin.core.request_handlers.ListViewRequestHandler',
                name='smadmin-list-view',
                methods=['GET'],
                schemes=['http', 'https']
            )
        )
        # Add the route for the detail view
        routes.append(
            webapp2.Route(
                r'{prefix}/{path}'.format(
                    prefix=smadmin.app.routes_prefix,
                    # Only get the last kind in the path component:
                    # (... , 'kind_n', id_n) -> 'kind_n'
                    # so we can access it at
                    # GET /admin/kind_n
                    path=r'/'.join(_path_components)
                ),
                handler='smadmin.core.request_handlers.DetailViewRequestHandler',
                name='smadmin-detail-view',
                methods=['GET'],
                schemes=['http', 'https']
            )
        )
        return routes
