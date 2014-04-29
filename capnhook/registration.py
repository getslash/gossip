import itertools

_registration_id = itertools.count()

class Registration(object):

    def __init__(self, func):
        super(Registration, self).__init__()
        self.id = next(_registration_id)
        self.func = func

    def can_be_called(self):
        return True

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
