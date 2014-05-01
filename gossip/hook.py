import logging

from ._compat import reraise
from .exceptions import RequirementsNotMet
from .registration import Registration

_logger = logging.getLogger(__name__)


class Hook(object):

    def __init__(self, name, arg_names=(), doc=None):
        super(Hook, self).__init__()
        self.name = name
        self._callbacks = []
        self._arg_names = arg_names
        self.doc = doc

    def get_argument_names(self):
        return self._arg_names

    def __call__(self, **kwargs):
        return self.trigger(kwargs)

    def register(self, func):
        self._callbacks.append(Registration(func))

    def trigger(self, kwargs):
        last_exc_info = None
        uncalled = [callback for callback in self._callbacks]
        while len(uncalled) > 0:
            found_fulfilled_callback = False
            remaining = []
            for callback in uncalled:
                if callback.can_be_called():
                    found_fulfilled_callback = True
                    exc_info = self._call_callback(callback, kwargs)
                    if last_exc_info is None:
                        last_exc_info = exc_info
                else:
                    remaining.append(callback)
            uncalled = remaining
            if not found_fulfilled_callback:
                raise RequirementsNotMet("Some callback requirements for {} could not be met".format(callback))
        if last_exc_info and not self._swallow_exceptions:
            _logger.debug("Reraising first exception in callback")
            reraise(*last_exc_info) # pylint: disable=W0142

    def _call_callback(self, callback, kwargs):
        exc_info = None
        try:
            callback(**kwargs) #pylint: disable=star-args
        except:
            exc_info = sys.exc_info()
            _logger.warn("Exception occurred while calling %s", callback, exc_info=exc_info)
            # TODO: debug here
        return exc_info

    def __repr__(self):
        return "<Hook {0}({1})>".format(self.name, ", ".join(self._arg_names))
