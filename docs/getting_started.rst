Getting Started
===============

This is a very simple guide to setup your first admin app.


Install The Admin
-----------------

1. Copy the admin framework somewhere in your Google App Engine project.
2. Make sure that the ``admin`` package is in the Python PATH.


Setup The Admin
---------------

In your Google App Engine project:

1. Open your app configuration file (``app.yaml``).

::

    handlers:
    # Existing handler
    - url: /.*
      script: api.app

2. In the handlers section, add a new app script and

::

    handlers:
    # New handlers
    - url: /admin/.*
      script: demo.app
    # Existing handler
    - url: /.*
      script: api.app

3. Also add the handler for the admin static files

::

    handlers:
    # New handlers
    - url: /admin/static
      static_dir: path_to_the_admin_folder/static
    - url: /admin/.*
      script: adminhandler.app
    # Existing handler
    - url: /.*
      script: api.app

4. In the same folder, create ``adminhandler.py``

::

    import smadmin as admin

    # Setup the app
    app = admin.app
    app.routes_prefix = '/admin'  # Matches the url config in app.yaml

5. At this point, the admin won't do much since there's no registered
   ``AdminModel``. So let's create a ``model_admin.py`` file:


::

    # model_admin.py

    # Import the admin
    import smadmin as admin

    # Import your existing ndb data model
    import models

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        # Don't do anything else and let the admin use the default settings.
        pass

6. You're one step away from having your first admin. Open your `models.py`
   file that defines ndb Models:

::

    # models.py

    class User(ndb.Model):
        created_on = ndb.DateTimeProperty(auto_now_add=True)
        updated_on = ndb.DateTimeProperty(auto_now=True)
        first_name = ndb.StringProperty()
        last_name = ndb.StringProperty()
        email = ndb.StringProperty()
        score = ndb.IntegerProperty()


In order to automatically register ndb Models, the admin needs to know how
entities are designed in your datastore.

An ndb entity is typically made of a kind and an integer ID or string name:

::

    # User keys
    ndb.Key('User', 42)
    ndb.Key('User', 'contact@starmakerinteractive.com')

But entities can also use ancestors, which slightly changes how keys look like:

::

    # Message key that belong to User 42
    ndb.Key('User', 42, 'Message', 1)

In order to do know that, we need your ndb.Model classes to define a specific
attribute, ``KEY_FORMAT``.
``KEY_FORMAT`` is similar to a flat Key, except that it uses Python types
instead of IDs/names so we know what those look like:

::

    class User(ndb.Model):
        KEY_FORMAT = ('User', int)
        # ...

For the case of the ``Message`` Key (``ndb.Key('User', 42, 'Message', 1)``), we
would do this in the ``Message`` class:

::

    class Message(ndb.Model):
        KEY_FORMAT = ('User', int, 'Message', int)
        # ...

For more information about ndb Keys and ancestors, read the Google App Engine
documentation:

* `NDB Entities and Keys article <https://cloud.google.com/appengine/docs/python/ndb/entities>`_
* `NDB Key Class <https://cloud.google.com/appengine/docs/python/ndb/keyclass>`_


**And there we go!** You now have a fully functional admin for your ``User`` model.


Use The Admin Locally
---------------------

Like any Google App Engine project, you can use the dev_appserver to test it on your machine:

::

    $ dev_appserver.py app.yaml
