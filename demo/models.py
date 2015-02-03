from google.appengine.ext import ndb
from admin import admin


# Standard ndb Models

class User(ndb.Model):

    # We're going to need that in order to know how to handle URL routing for
    # this entity model
    # For example, we'll have to handle these cases:
    # - List View:
    #     /admin/User/
    #     /admin/property_base/user_song-sm-42/user_song
    # - Detail View:
    #     /admin/User/42
    #     /admin/property_base/user_song-sm-42/user_song/1
    #
    # So we need that KEY_FORMAT in order to register those URL when we start
    # the app
    KEY_FORMAT = ('User', (int, long))

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    random_integer_value = ndb.IntegerProperty()


MCN_STATUS_FLOW_STARTED = 0
MCN_STATUS_GOOGLE_AUTHENTICATED = 1 << 0  # Stage Name & Google+ registration
MCN_STATUS_PERSONAL_INFO_COMPLETE = 1 << 1  # Age, name, etc
MCN_STATUS_CONTRACT_PRESENTED = 1 << 2  # A contract was generated for the user
MCN_STATUS_CONTRACT_COMPLETE = 1 << 3  # The contract was signed and validated
MCN_STATUS_USER_NOT_REJECTED = 1 << 4  # Bit set to 1 w/ CONTRACT COMPLETE
MCN_STATUS_YOUTUBE_INVITE_SENT = 1 << 5  # YouTube invite sent to the user
MCN_STATUS_YOUTUBE_INVITE_ACCEPTED = 1 << 6  # User completed the YT flow


class YouTubeUserInfo(ndb.Model):

    KEY_FORMAT = ('YouTubeUserInfo', basestring)

    cancelled = ndb.BooleanProperty()
    binary_statuses = ndb.IntegerProperty()
    statuses_keys = ndb.KeyProperty(
        kind='YouTubeUserStatus',
        repeated=True,
    )
    # Keep a reference to the deleted statuses keys
    deleted_statuses_keys = ndb.KeyProperty(
        kind='YouTubeUserStatus',
        repeated=True,
    )


class YouTubeUserInfoAdminListFilterByCancelled(admin.AdminListFilter):

    def form(self):
        form = admin.AdminListFilterFormSectionRadio(
            {'name': 'Yes', 'value': True},
            {'name': 'No', 'value': False}
        )
        return form

    def query(self, form):
        radio_checked = form.get_checked()
        query = YouTubeUserInfo.query(
            YouTubeUserInfo.canceled == radio_checked.value
        )
        return query


class YouTubeUserInfoAdminListFilterByBinaryStatus(admin.AdminListFilter):
    def form(self):
        form = admin.AdminListFilterFormSectionCheckbox(
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

        query = YouTubeUserInfo.query(
            YouTubeUserInfo.binary_statuses == mcn_status_value
        )
        return query


class YouTubeUserInfoAdminSearch(admin.AdminListSearch):
    placeholder = 'Search by MCN User ID or Channel Name'

    def search(self, search_string):
        results = []
        # Lookup the youtube_user_info
        try:
            youtube_user_info = YouTubeUserInfo.get_by_id(int(search_string))
            if youtube_user_info:
                results.append(results)
        except:
            pass
        # Lookup by channel ID
        youtube_user_info = YouTubeUserInfo.get_by_channel_id(search_string)
        if youtube_user_info:
            results.append(results)

        return results


class YouTubeUserInfoAdminActionCancel(admin.AdminBulkAction):

    name = 'Cancel MCN Users'

    @ndb.transactional
    def _cancel_youtube_user_info(self, key):
        youtube_user_info = key.get()
        if youtube_user_info is not None:
            youtube_user_info.cancelled = True
            youtube_user_info.put()

    def action(self, keys):
        for key in keys:
            self._cancel_youtube_user_info(key)


class YouTubeUserInfoAdminActionEnable(admin.AdminBulkAction):

    name = 'Enable MCN Users'

    @ndb.transactional
    def _cancel_mcn_user(self, key):
        youtube_user_info = key.get()
        if youtube_user_info is not None:
            youtube_user_info.cancelled = False
            youtube_user_info.put()

    def action(self, keys):
        for key in keys:
            self._cancel_mcn_user(key)


class YouTubeUserInfoAdminActionReject(admin.AdminBulkAction):

    name = 'Reject MCN Users'

    def action(self, keys):
        for key in keys:
            youtube_user_info = key.get()
            if youtube_user_info is None:
                continue
            # Assuming that youtube_user_info is wrapped
            youtube_user_info.add_status(MCN_STATUS_USER_NOT_REJECTED)
            youtube_user_info.add_status(MCN_STATUS_YOUTUBE_INVITE_SENT)


# Bind the YouTubeUserInfo model to this admin
@admin.register(YouTubeUserInfo)
class YouTubeUserInfoAdmin(admin.ModelAdmin):
    fields = (
        {
            'property': 'cancelled'
        }
    )
    filters = (
        YouTubeUserInfoAdminListFilterByCancelled,
        YouTubeUserInfoAdminListFilterByBinaryStatus,
    )
    actions = (
        YouTubeUserInfoAdminActionCancel,
        YouTubeUserInfoAdminActionEnable,
    )
    list_display = ('id', 'cancelled')
    list_display_links = ('id',)
