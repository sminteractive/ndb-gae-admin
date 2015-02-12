The AdminModel Class
====================


An admin model serves 3 main purposes:

* List all the entities that belong to the ndb Model
* Search or filter those entities
* Apply operations on those entities (which includes create / edit / delete)


So the goals of the AdminModel class are to:

* Configure how the listed entities are displayed
* Define how an admin user can search and filter those entities
* Provide the logic to apply some actions on entities


Setup An AdminModel
-------------------

The bare minimum configuration for an admin model is this:

::

    class MyAdmin(AdminModel):
        pass


But this model won't be usable until it's bound to an ndb Model:

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        pass

This is the only configuration you need to enable an admin for the
``User`` model.

But the ``AdminModel`` class allows you to customize what you want to display, and how the admin user can interact with the content.

We'll use a ``User`` ndb Model class for all our examples:

::

    class User(ndb.Model):
        created_on = ndb.DateTimeProperty(auto_now_add=True)
        updated_on = ndb.DateTimeProperty(auto_now=True)
        first_name = ndb.StringProperty()
        last_name = ndb.StringProperty()
        email = ndb.StringProperty()
        score = ndb.IntegerProperty()


Configure The List View
-----------------------

The list view has a few distinct components:

* The entity list
* The search tool
* The action tool (TBD)

The Entity List
^^^^^^^^^^^^^^^

The goal of this list is to let the user browse entities and quickly identify a specific row.


Configure The Columns
"""""""""""""""""""""

So defining which properties of the entities are be used as colums is instrumental to achieve that.

``AdminModel.list_display`` is a class attribute that offers you the possibility to restrict the set of properties displayed, and / or have control over the columns order:

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('email', 'first_name', 'last_name')

**Notes**

* You can insert ``'key'`` in the tuple to ask the admin to display the
  flat entity key.

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('key', 'email', 'first_name', 'last_name')

* If no ``AdminModel.list_display`` is defined in the Admin Model, every
  ndb property will be used as a column, ordered by name, and the first
  column will be the entity's key.


Configure The Links
"""""""""""""""""""

Listing entity is a great way to get informations on a large set of
data. But sometimes you want to get more information about a specific
entity, and open the Detail View.

The admin lets you configure which properties should be clickable to
open that view.

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('key', 'email', 'first_name', 'last_name')
        list_display_links = ('key', 'email')

**Notes**

* If no ``AdminModel.list_display_links`` is defined in the Admin
  Model, the ``key`` property will be used as the unique clickable item
  in the row.
* If we defined ``AdminModel.list_display`` that doesn't have
  ``'key'`` but no ``AdminModel.list_display_links`` attribute, the
  List View won't display links to any Detail View:

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('email', 'first_name', 'last_name')
        # The links to the detail views will be in the 'email' column

* If you define ``AdminModel.list_display_links`` elements that don't exist
  or are not visible, they'll just be ignored. In these cases, the List
  View won't display links to any Detail View:

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('first_name', 'last_name')
        list_display_links = ('email')

* If you define ``AdminModel.list_display_links`` elements that don't exist
  or are not visible, ``'key'`` won't be used as a link – even if it is defined
  in ``AdminModel.list_display``:

::

    @admin.register(models.User)
    class UserAdmin(admin.AdminModel):
        list_display = ('key', 'first_name', 'last_name')
        list_display_links = ('email')


The Search Tool
^^^^^^^^^^^^^^^

The search tool is instrumental to easily find the data you need.

