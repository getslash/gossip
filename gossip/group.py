from ._compat import itervalues
from .exception_policy import ExceptionPolicy, Inherit, RaiseImmediately
from .hook import Hook


class Group(object):

    def __init__(self, name, parent=None):
        super(Group, self).__init__()
        self.name = name
        self._parent = parent
        self.reset()

    def reset(self):
        self._hooks = {}
        self._subgroups = {}
        self._parent_exception_policy = None
        self.set_exception_policy(RaiseImmediately() if self._parent is None else Inherit())

    def notify_parent_exception_policy_changed(self):
        self._parent_exception_policy = None

    def create_hook(self, name):
        assert name not in self._hooks
        hook = Hook(self, name)
        self._hooks[name] = hook
        return hook

    def get_or_create_subgroup(self, name):
        returned = self._subgroups.get(name)
        if returned is None:
            returned = self._subgroups[name] = Group(name, parent=self)
        return returned

    def remove_all_children(self):
        self._hooks.clear()

    def set_exception_policy(self, policy):
        """ Determines how exceptions are handled by hooks in this group
        """
        if not isinstance(policy, ExceptionPolicy):
            raise ValueError("Expected ExceptionPolicy instance. Got {0!r}".format(policy))
        if isinstance(policy, Inherit) and self._parent is None:
            raise RuntimeError("Global gossip group cannot inherit exception policy from parent")

        self._exception_policy = policy
        for subgroup in itervalues(self._subgroups):
            subgroup.notify_parent_exception_policy_changed()

    def get_exception_policy(self):
        """Returns the current exception policy to be used by this group
        """
        if isinstance(self._exception_policy, Inherit):
            returned = self._parent_exception_policy
            if returned is None:
                returned = self._parent_exception_policy = self._parent.get_exception_policy()
            return returned
        return self._exception_policy

    def __repr__(self):
        return "<Gossip group {0!r}>".format(self.name)
