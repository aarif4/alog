"""Error classes"""

class aLogBaseError(Exception):
    """Base exception class for aLog errors.
    Parameters
    ----------
    msg : string
        Description of the error.
    """
    strerror : str

    def __init__(self, msg):
        """Wrap an errno style error.
        Parameters
        ----------
        msg : string
            Description of the error.
        """
        self.strerror = str(msg)

    def __str__(self):
        return self.strerror

    def __repr__(self):
        return f"{self.__class__.__name__}('{str(self)}')"

class aLogInputArgError(aLogBaseError):
    """Excpetion when input arguments are invalid"""
    pass

__all__ = [
    "aLogBaseError",
    "aLogInputArgError"
]