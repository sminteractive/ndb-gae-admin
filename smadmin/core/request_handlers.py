import webapp2

from . import adminmodel


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
        list_model = adminmodel.get_model_from_request_handler_parameters(
            partial_key_items)
        return webapp2.Response('/'.join(partial_key_items))

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
