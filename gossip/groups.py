from . import registry
from ._compat import itervalues, iteritems
from .exception_policy import ExceptionPolicy, Inherit, RaiseImmediately
from .exceptions import GroupNotFound, NameAlreadyUsed
from .helpers import DONT_CARE


class Group(object):

    def __init__(self, name, parent=None):
        super(Group, self).__init__()
        self.name = name
        self._parent = parent
        if self._parent is not None and not self._parent.is_global():
            self.full_name = "{0}.{1}".format(
                self._parent.full_name, self.name)
        else:
            self.full_name = name
        self.reset()

    def is_global(self):
        return self._parent is None

    def is_strict(self):
        return self._strict

    def undefine(self):
        self.undefine_children()
        if self._parent is not None:
            self._parent.remove_child(self.name)
        registry.groups.pop(self.full_name)

    def reset(self):
        if hasattr(self, "_children"):
            self.undefine_children()
        self._strict = False
        self._unconstrained_handler_priority = DONT_CARE
        self._children = {}
        self._parent_exception_policy = None
        self.set_exception_policy(
            RaiseImmediately() if self._parent is None else Inherit())

    def set_unconstrained_handler_priority(self, priority):
        """Controls when handlers without needs/provides specifications should be fired
        relative to handlers with needs/provides.

        :param priority: ``gossip.FIRST`` means that unconstrained handlers should be fired first, ``gossip.LAST`` means last
        """
        self._unconstrained_handler_priority = priority
        for hook in self.iter_hooks():
            hook.recompute_call_order()
        for group in self.iter_subgroups():
            group.set_unconstrained_handler_priority(priority)

    def get_unconstrained_handler_priority(self):
        return self._unconstrained_handler_priority

    def undefine_children(self):
        for child in list(itervalues(self._children)):
            child.undefine()

    def set_strict(self, strict=True):
        """Marks this group as a strict group, meaning all hooks registered must be defined in advance

        :param strict: controls whether or not this group should be turned to strict
        """
        for child in itervalues(self._children):
            if isinstance(child, Group):
                child.set_strict(strict)
            elif strict:
                child.validate_strict()
        self._strict = strict

    def get_undefined_hooks(self):
        returned = [
            hook for hook in self.get_hooks() if not hook.is_defined()]
        for group in self.get_subgroups():
            returned.extend(group.get_undefined_hooks())
        return returned

    def notify_parent_exception_policy_changed(self):
        self._parent_exception_policy = None

    def add_child(self, name, child):
        self._children[name] = child
        return child

    def remove_child(self, child):
        self._children.pop(child)

    def get_or_create_subgroup(self, name):
        returned = self._subgroups.get(name)
        if returned is None:
            returned = self._subgroups[name] = Group(name, parent=self)
        return returned

    def get_subgroups(self):
        return list(self.iter_subgroups())

    def iter_subgroups(self):
        for child in itervalues(self._children):
            if isinstance(child, Group):
                yield child

    def get_hooks(self):
        return list(self.iter_hooks())

    def iter_hooks(self):
        for child in itervalues(self._children):
            if isinstance(child, Group):
                continue
            yield child

    def remove_all_children(self):
        self._children.clear()

    def unregister_token(self, token):
        """Unregisters all handlers that were registered with ``token`` in this group
        """
        # todo: optimize this
        for hook in self.iter_hooks():
            for registration in hook.get_registrations():
                if registration.token == token:
                    registration.invalidate()
                    registration.unregister()
        for group in self.iter_subgroups():
            group.unregister_token(token)

    def set_exception_policy(self, policy):
        """ Determines how exceptions are handled by hooks in this group
        """
        if not isinstance(policy, ExceptionPolicy):
            raise ValueError(
                "Expected ExceptionPolicy instance. Got {0!r}".format(policy))
        if isinstance(policy, Inherit) and self._parent is None:
            raise RuntimeError(
                "Global gossip group cannot inherit exception policy from parent")

        self._exception_policy = policy
        for subgroup in self.iter_subgroups():
            subgroup.notify_parent_exception_policy_changed()

    def get_exception_policy(self):
        """Returns the current exception policy to be used by this group
        """
        if isinstance(self._exception_policy, Inherit):
            returned = self._parent_exception_policy
            if returned is None:
                returned = self._parent_exception_policy = self._parent.get_exception_policy(
                )
            return returned
        return self._exception_policy

    def __repr__(self):
        return "<Gossip group {0!r}>".format(self.name)


def get_global_group():
    """Gets the global (or root) group
    """
    return get_group(None)


def get_groups():
    """Gets all defined groups (including the global group)
    """
    return list(group for group_name, group in iteritems(registry.groups) if group_name is not None)


def get_or_create_group(name):
    """Tries to retrieve an existing group, and if it doesn't exist, create a new group
    """
    try:
        return get_group(name)
    except GroupNotFound:
        return create_group(name)


def get_group(name):
    """Returns an existing group with a given name

    :raises: KeyError if no such group exists
    """
    try:
        return registry.groups[name]
    except KeyError:
        raise GroupNotFound(name)


def create_group(name):
    """Creates and returns a new named group

    :rtype: :class:`gossip.group.Group`
    """
    if name in registry.groups:
        raise NameAlreadyUsed(
            "Group with name {0} already exists".format(name))

    if name in registry.hooks is not None:
        raise NameAlreadyUsed(
            "Hook with name {0} already exists. Cannot create group with same name".format(name))

    if "." in name:
        parent_name, group_name = name.rsplit(".", 1)
        parent = get_or_create_group(parent_name)
    else:
        parent = get_global_group()
        group_name = name

    group = Group(group_name, parent=parent)
    registry.groups[name] = group
    parent.add_child(group_name, group)
    return group


def unregister_token(token):
    """Shortcut for :func:`gossip.groups.Group.unregister_token` on the global group
    """
    get_global_group().unregister_token(token)

# Create the global group
registry.groups[None] = Group("**GLOBAL**")
