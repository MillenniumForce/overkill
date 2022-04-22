"""Module contains server exceptions for when things go wrong"""

class WorkerAlreadyExistsError(Exception):
    """Raise this error when trying to instantiate a new worker"""


class AskTypeNotFoundError(TypeError):
    """Raise this error when the 'type' of the ask could not be processed"""


class ServerNotStartedError(Exception):
    """Raise this error when an execption needs to be raised when a server hasn't been started"""


class WorkError(Exception):
    """Raise this error when the worker encounters an error when trying to
    execute the user's aray on the function"""


class NoWorkersError(Exception):
    """Raise this error when there are no workers connected to Master and
    the user tries to ask for work"""

class ServerAlreadyStartedError(Exception):
    """Raise this error when the user tries to start another server in the same class"""