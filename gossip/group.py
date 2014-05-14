import itertools

from ._compat import itervalues
from .exception_policy import ExceptionPolicy, Inherit, RaiseImmediately
from .exceptions import UndefinedHook
from .hook import Hook


class Group(object):

    def __init__(self, name, parent=None):
        super(Group, self).__init__()
        self.name = name
        self._parent = parent
        if self._parent is not None and not self._parent.is_global():
            self.full_name = "{0}.{1}".format(self._parent.full_name, self.name)
        else:
            self.full_name = name
        self.reset()

    def is_global(self):
        return self._parent is None

    def reset(self):
        self._strict = False
        self._hooks = {}
        self._subgroups = {}
        self._parent_exception_policy = None
        self.set_exception_policy(RaiseImmediately() if self._parent is None else Inherit())

    def set_strict(self):
        """Marks this group as a strict group, meaning all hooks registered must be defined in advance"""
        undefined = self.get_undefined_hooks()
        if undefined:
            raise UndefinedHook("Undefined hook{0}: {1}".format("s" if len(undefined) > 1 else "", ", ".join(hook.full_name for hook in undefined)))
        self._strict = True

    def get_undefined_hooks(self):
        returned = [hook for hook in itervalues(self._hooks) if not hook.is_defined()]
        for group in itervalues(self._subgroups):
            returned.extend(group.get_undefined_hooks())
        return returned

    def is_strict(self):
        return self._strict

    def notify_parent_exception_policy_changed(self):
        self._parent_exception_policy = None

    def create_hook(self, name, **kwargs):
        assert name not in self._hooks
        hook = Hook(self, name, **kwargs)
        self._hooks[name] = hook
        return hook

    def get_or_create_subgroup(self, name):
        returned = self._subgroups.get(name)
        if returned is None:
            returned = self._subgroups[name] = Group(name, parent=self)
        return returned

    def get_all_hooks(self):
        returned = list(itervalues(self._hooks))
        for group in itervalues(self._subgroups):
            returned.extend(group.get_all_hooks())
        return returned

    def get_all_registrations(self):
        return [registration for hook in self.get_all_hooks() for registration in hook.get_registrations()]

    def get_subgroups(self):
        return list(itervalues(self._subgroups))

    def remove_all_children(self):
        self._hooks.clear()
        self._subgroups.clear()

    def unregister_all(self):
        """Unregisters all handlers in all hooks in all subgroups of this group
        """
        for child in itertools.chain(itervalues(self._hooks), itervalues(self._subgroups)):
            child.unregister_all()

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
