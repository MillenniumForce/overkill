"""Module contains server exceptions for when things go wrong"""

class WorkerAlreadyExistsError(Exception):
    """Raise this error when trying to instantiate a new worker"""

class AskTypeNotFoundError(TypeError):
    """Raise this error when the 'type' of the ask could not be processed"""

class ServerNotStartedError(Exception):
    """Raise this error when an execption needs to be raised when a server hasn't been started"""