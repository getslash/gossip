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
    pass

class UndefinedHook(Exception):
    pass

class UnsupportedHookTags(Exception):
    pass
