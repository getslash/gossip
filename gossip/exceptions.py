class HookException(Exception):
    pass

class NameAlreadyUsed(HookException):
    pass

class HookNotFound(LookupError):
    pass

class GroupNotFound(LookupError):
    pass

class NotNowException(Exception):
    pass

class CannotResolveDependencies(Exception):
    def __init__(self, *args, **kwargs):
        self.unmet_dependencies = kwargs.pop('unmet_deps', None)
        super(CannotResolveDependencies, self).__init__(*args, **kwargs)

class CannotMuteHooks(Exception):
    pass

class UndefinedHook(Exception):
    pass

class UnsupportedHookTags(Exception):
    pass

class UnsupportedHookParams(Exception):
    pass
