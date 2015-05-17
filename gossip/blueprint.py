from uuid import uuid4

from . import hooks
from . import groups


class Blueprint(object):
    """Represents a hook blueprint

    Blueprints are sets of hooks that can be registered or unregistered with a single operation.
    """

    def __init__(self):
        super(Blueprint, self).__init__()
        self._hooks = []
        self._token = str(uuid4())

    def register(self, hook_name, **kwargs):
        """Registers a function to this blueprint

        .. seealso:: :func:`gossip.register`
        """
        def decorator(func):
            self._hooks.append((hook_name, func, kwargs))
            return func
        return decorator

    def install(self, group=None):
        """Installs the blueprint, registering all of its handlers to their respective hooks
        """
        try:
            for hook_name, func, kwargs in self._hooks:
                if group is not None:
                    hook_name = '{0}.{1}'.format(group, hook_name)
                hooks.register(func=func, hook_name=hook_name, token=self._token, **kwargs)
        except:
            self.uninstall()
            raise

    def uninstall(self):
        """Uninstalls the blueprint, unregistering all of its hooks
        """
        groups.unregister_token(self._token)
