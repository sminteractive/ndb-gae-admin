from google.appengine.ext import ndb


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
    KEY_FORMAT = ('User', int)

    updated_on = ndb.DateTimeProperty(auto_now=True)

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


class PropertyBase(ndb.Model):
    KEY_FORMAT = ('PropertyBase', int)


class EntityWithAncestor(ndb.Model):
    KEY_FORMAT = ('PropertyBase', int, 'EntityWithAncestor', int)


# for u in User.query():
#     u.key.delete()
# for x in xrange(101):
#     User(
#         id=3 * x,
#         first_name='JC' + str(x),
#         last_name='Lanoe',
#         email='jc.lanoe@starmakerinteractive.com',
#         random_integer_value=42,
#     ).put()
#     User(
#         id=3 * x + 1,
#         first_name='Alex' + str(x),
#         last_name='Jolicoeur',
#         email='alex.jolicoeur@starmakerinteractive.com',
#         random_integer_value=127,
#     ).put()
#     User(
#         id=3 * x + 2,
#         first_name='Nicholas' + str(x),
#         last_name='Charriere',
#         email='nicholas.charriere@starmakerinteractive.com',
#         random_integer_value=512,
#     ).put()
