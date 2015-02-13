import smadmin as admin
import demo_models as models


# class YouTubeUserInfoAdminActionCancel(smadmin.AdminBulkAction):

#     name = 'Cancel MCN Users'

#     @ndb.transactional
#     def _cancel_youtube_user_info(self, key):
#         youtube_user_info = key.get()
#         if youtube_user_info is not None:
#             youtube_user_info.cancelled = True
#             youtube_user_info.put()

#     def action(self, keys):
#         for key in keys:
#             self._cancel_youtube_user_info(key)


# class YouTubeUserInfoAdminActionEnable(smadmin.AdminBulkAction):

#     name = 'Enable MCN Users'

#     @ndb.transactional
#     def _cancel_mcn_user(self, key):
#         youtube_user_info = key.get()
#         if youtube_user_info is not None:
#             youtube_user_info.cancelled = False
#             youtube_user_info.put()

#     def action(self, keys):
#         for key in keys:
#             self._cancel_mcn_user(key)


# class YouTubeUserInfoAdminActionReject(smadmin.AdminBulkAction):

#     name = 'Reject MCN Users'

#     def action(self, keys):
#         for key in keys:
#             youtube_user_info = key.get()
#             if youtube_user_info is None:
#                 continue
#             # Assuming that youtube_user_info is wrapped
#             youtube_user_info.add_status(models.MCN_STATUS_USER_NOT_REJECTED)
#             youtube_user_info.add_status(models.MCN_STATUS_YOUTUBE_INVITE_SENT)


# Bind the YouTubeUserInfo model to this admin
@admin.register(models.YouTubeUserInfo)
class YouTubeUserInfoAdmin(admin.AdminModel):
    pass


@admin.register(models.EntityWithAncestor)
class EntityWithAncestorAdmin(admin.AdminModel):
    pass


class SearchUserByEmail(admin.ListViewSearch):
    title = 'Search by ID or email'

    def form(self):
        return admin.html.Form(
            admin.html.InputGoup(
                admin.html.Input(name='search_user_by_email')
            )
        )

    def filter(self, data, cursor):
        pass


class SearchUserByFirstName(admin.ListViewSearch):
    title = 'Search by First Name'


class SearchUserByLastName(admin.ListViewSearch):
    title = 'Search by Last Name'


@admin.register(models.User)
class UserAdmin(admin.AdminModel):
    list_display = ('first_name', 'last_name', 'email')
    # list_display_links = ('key', 'last_name')

    detail_display = (
        'updated_on',
        'first_name',
        'last_name',
        'email',
        'random_integer_value',
    )
    detail_readonly = (
        'updated_on',
    )

    # default_search_enabled = False

    # list_searches = [
    #     SearchUserByEmail
    # ]

    # @classmethod
    # def search(cls, search_string, cursor, mode=None):
    #     # Paginated search by first name
    #     if mode == cls.SEARCH_MODE_FIRST_NAME:
    #         query = cls.model.query(cls.model.first_name == search_string)
    #         return query.fetch_page(50, start_cursor=cursor)
    #     # Paginated search by larst name
    #     elif mode == cls.SEARCH_MODE_LAST_NAME:
    #         query = cls.model.query(cls.model.last_name == search_string)
    #         return query.fetch_page(50, start_cursor=cursor)
    #     # Default search
    #     # Custom query with potentially multiple small queries (so no cursor)
    #     elif mode == cls.SEARCH_MODE_DEFAULT:
    #         searched_entities = []
    #         # Search by ID
    #         try:
    #             user_id = int(search_string)
    #             user = cls.model.get_by_id(user_id)
    #             if user is not None:
    #                 searched_entities.append(user)
    #         except Exception:
    #             pass
    #         for user in cls.model.query(cls.model.email == search_string):
    #             searched_entities.append(user)
    #         return searched_entities, None, False

    #     # Default to an empty result
    #     return [], None, False
