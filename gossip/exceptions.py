class HookException(Exception):
    pass

class NameAlreadyUsed(HookException):
    pass

class HookNotFound(LookupError):
    pass
