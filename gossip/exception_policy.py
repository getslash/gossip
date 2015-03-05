import sys
from contextlib import contextmanager

from ._compat import reraise


class ExceptionPolicy(object):

    @contextmanager
    def context(self):
        ctx = TriggerContext()
        try:
             yield ctx
        except:
            exc_info = sys.exc_info()
            self.handle_exception(ctx, exc_info)
        self._handle_trigger_end(ctx)

    def handle_exception(self, ctx, exc_info):
        ctx.exceptions.append(exc_info)

    def _handle_trigger_end(self, ctx):
        pass

class RaiseImmediately(ExceptionPolicy):

    def handle_exception(self, ctx, exc_info):
        reraise(exc_info[0], exc_info[1], exc_info[2])

class RaiseDefer(ExceptionPolicy):

    def _handle_trigger_end(self, ctx):
        if ctx.exceptions:
            exc_type, exc_value, exc_tb = ctx.exceptions[0]
            reraise(exc_type, exc_value, exc_tb)

class IgnoreExceptions(ExceptionPolicy):
    pass

class Inherit(ExceptionPolicy):
    pass

class TriggerContext(object):

    def __init__(self):
        super(TriggerContext, self).__init__()
        self.exceptions = []
