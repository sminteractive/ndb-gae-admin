from admin.core.errors import AbstractClassError


class ModelAdmin(object):
    fields = ()
    filters = ()
    actions = ()
    list_display = ()
    list_display_links = ()

    def __init__(self, *args, **kwargs):
        raise AbstractClassError()

    def generate_routes(self):
        routes = []
        # Add the route for the list view
        routes.append(
            '/{}'
        )
