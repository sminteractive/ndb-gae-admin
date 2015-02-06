import smadmin
import demo_models as models


class YouTubeUserInfoAdminListFilterByCancelled(smadmin.AdminListFilter):

    def form(self):
        form = smadmin.AdminListFilterFormRadio(
            {'name': 'Yes', 'value': True},
            {'name': 'No', 'value': False}
        )
        return form

    def query(self, form):
        radio_checked = form.get_checked()
        query = models.YouTubeUserInfo.query(
            models.YouTubeUserInfo.canceled == radio_checked.value
        )
        return query


class YouTubeUserInfoAdminListFilterByBinaryStatus(smadmin.AdminListFilter):
    def form(self):
        form = smadmin.AdminListFilterFormCheckbox(
            # Creates a FormCheckbox object
            {'name': 'Flow Started', 'value': 0},
            {'name': 'Google Authenticated', 'value': 1},
            {'name': 'Personal Info Complete', 'value': 2},
            {'name': 'Contract Presented', 'value': 4},
            {'name': 'Contract Signed', 'value': 16},
            {'name': 'User Rejected', 'value': 8},
            {'name': 'Invite Sent', 'value': 32},
            {'name': 'Invite Accepted', 'value': 64},
            identifier='mcn_statuses',
            name='MCN Statuses',
        )
        return form

    def query(self, form):
        form_section = form.get_section('MCN Statuses')
        mcn_status_value = 0
        for checkbox in form_section:
            if checkbox.checked:
                mcn_status_value = mcn_status_value | checkbox.value

        query = models.YouTubeUserInfo.query(
            models.YouTubeUserInfo.binary_statuses == mcn_status_value
        )
        return query


class YouTubeUserInfoAdminSearch(smadmin.AdminListSearch):
    placeholder = 'Search by MCN User ID or Channel Name'

    def search(self, search_string):
        results = []
        # Lookup the youtube_user_info
        try:
            youtube_user_info = models.YouTubeUserInfo.get_by_id(
                int(search_string))
            if youtube_user_info:
                results.append(results)
        except:
            pass
        # Lookup by channel ID
        youtube_user_info = models.YouTubeUserInfo.get_by_channel_id(
            search_string)
        if youtube_user_info:
            results.append(results)

        return results


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
@smadmin.register(models.YouTubeUserInfo, models.EntityWithAncestor)
class YouTubeUserInfoAdmin(smadmin.ModelAdmin):
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


@smadmin.register(models.User)
class UserAdmin(smadmin.ModelAdmin):
    list_display = ('key', 'first_name', 'last_name', 'email')
