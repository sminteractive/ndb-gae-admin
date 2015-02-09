import os

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.datastore.datastore_query import Cursor

import smadmin
from . import adminmodel


def get_detail_view_path_for_entity(entity):
    return '{}/{}'.format(
        smadmin.app.routes_prefix,
        '/'.join([str(e) for e in entity.key.flat()])
    )


class HomeViewRequestHandler(webapp2.RequestHandler):

    def get(self):
        path = os.path.join(
            os.path.dirname(__file__),
            '../templates/home_view.html'
        )
        rendered_template = template.render(path, {'app': smadmin.app})
        return webapp2.Response(rendered_template)


class ListViewRequestHandler(webapp2.RequestHandler):

    def _create_query_strings(
            self,
            next_cursor,
            more,
            previous_cursor_url_safe,
            has_previous):
        '''
        Returns the previous and next page formatted query string parameters.

        Args:
            next_cursor: ndb Cursor, may be None.

            more: bool, tells if there's a next page.

            previous_cursor_url_safe: string, URL safe cursor string.
                                      May be None.

            has_previous: bool, tells if there's a previous page.

        Returns:
            previous_page_qs, next_page_qs
        '''
        # Initialize the list of query string elements
        next_page_qs_items = []
        previous_page_qs_items = []
        if next_cursor is not None and more:
            next_page_qs_items.append(
                'cursor={}'.format(
                    next_cursor.urlsafe() if next_cursor is not None and more
                    else None
                )
            )
        if has_previous and previous_cursor_url_safe:
            previous_page_qs_items.append(
                'cursor={}'.format(previous_cursor_url_safe)
            )
        if next_cursor is not None and more:
            if self.request.GET.get('search'):
                next_page_qs_items.append(
                    'search={}'.format(self.request.GET.get('search'))
                )
            if self.request.GET.get('search_mode'):
                next_page_qs_items.append(
                    'search_mode={}'.format(
                        self.request.GET.get('search_mode'))
                )
        if has_previous:
            if self.request.GET.get('search_mode'):
                previous_page_qs_items.append(
                    'search={}'.format(self.request.GET.get('search'))
                )
            if self.request.GET.get('search_mode'):
                previous_page_qs_items.append(
                    'search_mode={}'.format(
                        self.request.GET.get('search_mode'))
                )

        # Default links to None so the template know that it should not enable
        # the previous / next page
        previous_page_qs = '?'
        next_page_qs = '?'
        if previous_page_qs_items:
            previous_page_qs += '{}'.format(
                '&'.join((previous_page_qs_items)))
        if next_page_qs_items:
            next_page_qs += '{}'.format('&'.join((next_page_qs_items)))

        return previous_page_qs, next_page_qs

    def _create_response(
            self,
            model,
            admin_model,
            cursor,
            entities,
            next_cursor,
            more):
        # Admin properties to display in the list
        if not admin_model.list_display:
            properties_to_diplay = [
                k for k, v in model.__dict__.iteritems()
                if isinstance(v, ndb.Property)
            ]
            properties_to_diplay.sort()
            properties_to_diplay.insert(0, 'key')
        else:
            properties_to_diplay = admin_model.list_display

        # Save the previous cursor in memcache so we can go back
        if next_cursor is not None and more:
            # Keep a reference of the page before the one loaded with the
            # "next_cursor" cursor, so we can go back on the next page
            memcache.set(
                next_cursor.urlsafe(),
                # The second page's previous page must be marked differently
                # so we know that we can go back, but also that there's no
                # cursor needed
                #
                # Note:
                # Directly saving the cursor in memcache as an ndb Cursor
                # object leads to memcache misses, so we always call urlsafe()
                # on it before.
                cursor.urlsafe() if cursor is not None else 0,
                namespace='smadmin_previous_cursors'
            )

        previous_cursor_url_safe = None
        has_previous = False
        if cursor is not None:
            previous_cursor_url_safe = memcache.get(
                cursor.urlsafe(),
                namespace='smadmin_previous_cursors'
            )
            if previous_cursor_url_safe is not None:
                has_previous = True
            if previous_cursor_url_safe == 0:
                previous_cursor_url_safe = None

        # Build entities links
        links = []
        for entity in entities:
            link = get_detail_view_path_for_entity(entity)
            links.append(link)

        # Create query string parameters for the previous and next page
        previous_page_qs, next_page_qs = self._create_query_strings(
            next_cursor,
            more,
            previous_cursor_url_safe,
            has_previous
        )

        # Default search mode (optional)
        default_search_mode = None
        if admin_model.search_modes:
            if 'default' in admin_model.search_modes:
                default_search_mode = 'default'
            else:
                # admin_model.search_modes[0] == ('custom_mode': Search by...)
                default_search_mode = admin_model.search_modes[0][0]

        # Build template
        path = os.path.join(
            os.path.dirname(__file__),
            '../templates/list_view.html'
        )
        rendered_template = template.render(
            path,
            {
                # App parameters
                'app': smadmin.app,
                'model': model,
                'model_name': model.__name__,
                'admin_model': admin_model,
                # Entities parameters
                'properties': properties_to_diplay,
                'entities_and_links': zip(entities, links),
                'properties_with_link': admin_model.list_display_links,
                # Nvigation parameters
                'has_previous': has_previous,
                'has_next': next_cursor is not None and more,
                'previous_page_qs': previous_page_qs,
                'next_page_qs': next_page_qs,
                # Search parameters
                'is_search_enabled': admin_model.search is not None,
                'search_value': self.request.GET.get('search'),
                'current_search_mode': self.request.GET.get('search_mode'),
                'default_search_mode': default_search_mode,
                'search_modes': admin_model.search_modes,
            }
        )
        return webapp2.Response(rendered_template)

    def search_entities(self, admin_model, cursor):
        # Get the search string sent from the HTML form in the list view
        search_string = self.request.GET.get('search')

        # Get the optional search mode
        search_mode = self.request.GET.get('search_mode')

        # No op if the search string is missing or empty
        if admin_model.search is None or not search_string:
            return [], None, False  # entities, next_cursor, more

        # Call the search method defined in the admin
        _search_return_values = admin_model.search(
            search_string,
            cursor,
            search_mode
        )

        # Check that _search_return_values matches the expected return values
        if not isinstance(_search_return_values, (list, tuple)) \
                or len(_search_return_values) != 3:
            raise ValueError(
                'The search() method defined in the Admin Model {} must return'
                '3 values (entities, next_cursor, more)'
            )
        return _search_return_values

    def list_entities(self, model, cursor):
        # Get the entities
        query = model.query()
        return query.fetch_page(50, start_cursor=cursor)

    def get(self, *partial_key_items):
        '''
        /admin/{kind}[/{id}/{kind} ...]

        Examples:
            Simple Key (list all the users):
            /admin/end_user

            Complex Keys (list all the SM songs that belong to user 42):
            /admin/property_base/user_song-sm-42/user_song

        Params:
            partial_key_items: flat ndb Key.
                Examples:
                ('end_user',)
                ('property_base', 'user_song-sm-42', 'user_song')
        '''
        model = adminmodel.get_model_from_request_handler_parameters(
            partial_key_items)
        admin_model = adminmodel.get_admin_model_from_model(model)

        # Parse the ndb Cursor
        cursor = None
        url_cursor = self.request.GET.get('cursor')
        if url_cursor:
            try:
                cursor = Cursor(urlsafe=url_cursor)
            except Exception:
                cursor = None

        if self.request.GET.get('search'):
            entities, next_cursor, more = self.search_entities(
                admin_model,
                cursor
            )
        else:
            entities, next_cursor, more = self.list_entities(model, cursor)

        return self._create_response(
            model,
            admin_model,
            cursor,
            entities,
            next_cursor,
            more
        )

    def post(self, *key_items):
        pass


class DetailViewRequestHandler(webapp2.RequestHandler):

    def get(self, *key_items):
        '''
        /admin/{kind}/{id}[{kind}/{id} ...]

        Examples:
            Simple Key: /admin/end_user/42
            Complex Keys: /admin/property_base/user_song-sm-42/user_song/1

        Params:
            key_items: flat ndb Key.
                Examples:
                ('end_user', 42)
                ('property_base', 'user_song-sm-42', 'user_song', 1)
        '''
        model = adminmodel.get_entity_from_request_handler_parameters(
            key_items)
        admin_model = adminmodel.get_admin_model_from_model(model)
        path = os.path.join(
            os.path.dirname(__file__),
            '../templates/detail_view.html'
        )
        rendered_template = template.render(
            path,
            {
                # App parameters
                'app': smadmin.app,
                'model': model,
                'model_name': model.__name__,
                'admin_model': admin_model,
            }
        )
        return webapp2.Response(rendered_template)
