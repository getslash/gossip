FIRST = 'FIRST'
LAST = 'LAST'
DONT_CARE = 'DONT_CARE'


class Toggle(object):

    def __init__(self):
        super(Toggle, self).__init__()
        self._on = False

    def is_on(self):
        return self._on

    def is_off(self):
        return not self._on

    def toggle(self):
        self._on = not self._on
