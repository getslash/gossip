class HookException(Exception):
    pass

class RequirementsNotMet(HookException):
    pass

class NameAlreadyUsed(HookException):
    pass
