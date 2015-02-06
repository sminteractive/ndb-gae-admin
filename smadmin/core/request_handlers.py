import os

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.datastore.datastore_query import Cursor

import smadmin
from . import adminmodel


class HomeViewRequestHandler(webapp2.RequestHandler):

    def get(self):
        path = os.path.join(
            os.path.dirname(__file__),
            '../templates/home_view.html'
        )
        rendered_template = template.render(path, {'app': smadmin.app})
        return webapp2.Response(rendered_template)


class ListViewRequestHandler(webapp2.RequestHandler):

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

        if not admin_model.list_display:
            properties_to_diplay = [
                k for k, v in model.__dict__.iteritems()
                if isinstance(v, ndb.Property)
            ]
            properties_to_diplay.sort()
            properties_to_diplay.insert(0, 'key')
        else:
            properties_to_diplay = admin_model.list_display

        # Parse the ndb Cursor
        cursor = None
        url_cursor = self.request.GET.get('cursor')
        if url_cursor:
            try:
                cursor = Cursor(urlsafe=url_cursor)
            except Exception:
                cursor = None
        # Get the entities
        query = model.query()
        entities, next_cursor, more = query.fetch_page(50, start_cursor=cursor)

        # Save the previous cursor in memcache
        if next_cursor is not None:
            memcache.set(
                next_cursor.urlsafe(),
                cursor.urlsafe() if cursor is not None else 0,
                namespace='smadmin_previous_cursors'
            )
        previous_cursor = None
        has_previous = False
        if cursor is not None:
            previous_cursor = memcache.get(
                cursor.urlsafe(),
                namespace='smadmin_previous_cursors'
            )
            if previous_cursor is not None:
                has_previous = True
            if previous_cursor == 0:
                previous_cursor = None

        # Build Template
        path = os.path.join(
            os.path.dirname(__file__),
            '../templates/list_view.html'
        )
        rendered_template = template.render(
            path,
            {
                'app': smadmin.app,
                'model': model,
                'model_name': model.__name__,
                'admin_model': admin_model,
                'properties': properties_to_diplay,
                'entities': entities,
                'previous_cursor': previous_cursor,
                'next_cursor': next_cursor.urlsafe() if next_cursor and more else None,
                'has_previous': has_previous,
                'has_next': next_cursor and more,
            }
        )
        return webapp2.Response(rendered_template)

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
        entity_model = adminmodel.get_entity_from_request_handler_parameters(
            key_items)
        return webapp2.Response('/'.join(key_items))
