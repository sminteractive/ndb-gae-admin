
class AbstractClassError(Exception):
    def __init__(self, cls, *args, **kwargs):
        self.message = 'Class {} is abstract and cannot be instatiated'.format(
            cls.__name__
        )

    def __str__(self):
        return repr(self.message)


class NoModelKeyFormatError(Exception):
    def __init__(self, model, *args, **kwargs):
        self.message = 'ndb Model {} must have a KEY_FORMAT property to be ' \
            'bound with an Admin Model'.format(model.__name__)

    def __str__(self):
        return repr(self.message)


class InvalidModelKeyFormatError(Exception):
    def __init__(self, model, *args, **kwargs):
        self.message = 'ndb Model {} must have a KEY_FORMAT property that ' \
            'has an even number'.format(model.__name__)

    def __str__(self):
        return repr(self.message)
