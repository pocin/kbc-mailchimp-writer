"""
Custom exceptions

The final `run()` funtion captures all 

"""

class UserError(Exception):
    pass

class ConfigError(UserError):
    pass

class CleaningError(UserError):
    pass

class MissingFieldError(CleaningError):
    pass
