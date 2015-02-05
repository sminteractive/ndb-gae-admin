import smadmin

# Setup the app
# app (instance of AdminApplication) inherits of webapp2.WSGIApplication
app = smadmin.app
app.routes_prefix = '/adm'
app.discover_admins('demo_admin')
