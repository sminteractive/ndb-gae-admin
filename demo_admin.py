import smadmin as admin
import demo_models as models


# class YouTubeUserInfoAdminListFilterByCancelled(smadmin.AdminListFilter):
#     def form(self):
#         form = smadmin.AdminListFilterFormRadio(
#             {'name': 'Yes', 'value': True},
#             {'name': 'No', 'value': False}
#         )
#         return form

#     def query(self, form):
#         radio_checked = form.get_checked()
#         query = models.YouTubeUserInfo.query(
#             models.YouTubeUserInfo.canceled == radio_checked.value
#         )
#         return query


# class YouTubeUserInfoAdminListFilterByBinaryStatus(smadmin.AdminListFilter):
#     def form(self):
#         form = smadmin.AdminListFilterFormCheckbox(
#             # Creates a FormCheckbox object
#             {'name': 'Flow Started', 'value': 0},
#             {'name': 'Google Authenticated', 'value': 1},
#             {'name': 'Personal Info Complete', 'value': 2},
#             {'name': 'Contract Presented', 'value': 4},
#             {'name': 'Contract Signed', 'value': 16},
#             {'name': 'User Rejected', 'value': 8},
#             {'name': 'Invite Sent', 'value': 32},
#             {'name': 'Invite Accepted', 'value': 64},
#             identifier='mcn_statuses',
#             name='MCN Statuses',
#         )
#         return form

#     def query(self, form):
#         form_section = form.get_section('MCN Statuses')
#         mcn_status_value = 0
#         for checkbox in form_section:
#             if checkbox.checked:
#                 mcn_status_value = mcn_status_value | checkbox.value

#         query = models.YouTubeUserInfo.query(
#             models.YouTubeUserInfo.binary_statuses == mcn_status_value
#         )
#         return query


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
    # fields = (
    #     {
    #         'property': 'cancelled'
    #     }
    # )
    # filters = (
    #     YouTubeUserInfoAdminListFilterByCancelled,
    #     YouTubeUserInfoAdminListFilterByBinaryStatus,
    # )
    # actions = (
    #     # YouTubeUserInfoAdminActionCancel,
    #     # YouTubeUserInfoAdminActionEnable,
    # )
    # list_display = ('id', 'cancelled')
    # list_display_links = ('id',)
    pass


@admin.register(models.EntityWithAncestor)
class EntityWithAncestorAdmin(admin.AdminModel):
    pass


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

    SEARCH_MODE_DEFAULT = 'default'
    SEARCH_MODE_FIRST_NAME = 'first_name'
    SEARCH_MODE_LAST_NAME = 'last_name'
    # We use a list to have control over the display order
    search_modes = [
        (SEARCH_MODE_DEFAULT, 'Search by ID or email'),  # custom qry w/o curs
        (SEARCH_MODE_FIRST_NAME, 'Search by First Name'),  # query with cursor
        (SEARCH_MODE_LAST_NAME, 'Search by Last Name'),  # query with cursor
    ]

    @classmethod
    def search(cls, search_string, cursor, mode=None):
        # Paginated search by first name
        if mode == cls.SEARCH_MODE_FIRST_NAME:
            query = cls.model.query(cls.model.first_name == search_string)
            return query.fetch_page(50, start_cursor=cursor)
        # Paginated search by larst name
        elif mode == cls.SEARCH_MODE_LAST_NAME:
            query = cls.model.query(cls.model.last_name == search_string)
            return query.fetch_page(50, start_cursor=cursor)
        # Default search
        # Custom query with potentially multiple small queries (so no cursor)
        elif mode == cls.SEARCH_MODE_DEFAULT:
            searched_entities = []
            # Search by ID
            try:
                user_id = int(search_string)
                user = cls.model.get_by_id(user_id)
                if user is not None:
                    searched_entities.append(user)
            except Exception:
                pass
            for user in cls.model.query(cls.model.email == search_string):
                searched_entities.append(user)
            return searched_entities, None, False

        # Default to an empty result
        return [], None, False
