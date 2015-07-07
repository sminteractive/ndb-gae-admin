from google.appengine.ext.webapp import template


register = template.create_template_register()


def _getattr(obj, value):
    '''
    {% load getattr %}
    {{ object|getattr:dynamic_string_var }}
    '''
    return getattr(obj, value, None)


def getlistitem(list_object, index):
    return list_object[index]

register.filter('getattr', _getattr)
register.filter('getlistitem', getlistitem)
