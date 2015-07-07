
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
            'has an even number of items'.format(model.__name__)

    def __str__(self):
        return repr(self.message)


class EmptySearchError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = 'The List View Search could not be processed because ' \
            'it doesn\'t have enough info'

    def __str__(self):
        return repr(self.message)
