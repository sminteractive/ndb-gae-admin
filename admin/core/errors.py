
class AbstractClassError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = 'Class is abstract and cannot be instatiated'

    def __str__(self):
        return repr(self.message)
