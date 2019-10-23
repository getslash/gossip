FIRST = 'FIRST'
LAST = 'LAST'
DONT_CARE = 'DONT_CARE'


class Toggle():

    def __init__(self):
        super().__init__()
        self._on = False

    def is_on(self):
        return self._on

    def is_off(self):
        return not self._on

    def toggle(self):
        self._on = not self._on
