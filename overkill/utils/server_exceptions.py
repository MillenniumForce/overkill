class workerAlreadyExistsError(Exception):
    """Raise this error when trying to instantiate a new worker"""

class askTypeNotFoundError(TypeError):
    """Raise this error when the 'type' of the ask could not be processed"""