import webapp2


class AdminApplication(webapp2.WSGIApplication):

    def __init__(self, routes_prefix='', *args, **kwargs):
        super(self, AdminApplication).__init__(*args, **kwargs)
        self.registered_models = {}
        self.routes_prefix = routes_prefix

    def register(self, model_admin, model):
        self.registered_models[model.__name__] = model_admin
        self.router.add(
            webapp2.Route(
                u'{}'
            )
        )


# Enabled PATCH method
# http://stackoverflow.com/questions/16280496
allowed_methods = AdminApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
AdminApplication.allowed_methods = new_allowed_methods


app = AdminApplication()
