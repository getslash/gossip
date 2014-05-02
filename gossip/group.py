from .hook import Hook


class Group(object):

    def __init__(self, name):
        super(Group, self).__init__()
        self.name = name
        self._hooks = {}
        self._subgroups = {}

    def create_hook(self, name):
        assert name not in self._hooks
        hook = Hook(self, name)
        self._hooks[name] = hook
        return hook

    def get_or_create_subgroup(self, name):
        returned = self._subgroups.get(name)
        if returned is None:
            returned = self._subgroups[name] = Group(name)
        return returned

    def remove_all_children(self):
        self._hooks.clear()

    def __repr__(self):
        return "<Gossip group {0!r}>".format(self.name)
