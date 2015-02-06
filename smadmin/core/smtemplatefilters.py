from google.appengine.ext.webapp import template


register = template.create_template_register()


def _getattr(obj, value):
    '''
    {% load getattr %}
    {{ object|getattr:dynamic_string_var }}
    '''
    return getattr(obj, value, None)


register.filter('getattr', _getattr)
