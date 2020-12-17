import logging
from typing import Optional

__all__ = ["error", "new_error"]


class _Error:

    def __init__(self, text: str, error_code: int = -1):
        self._text = text
        self.error_code = error_code

    def __str__(self):
        return self._text

    def __repr__(self):
        return f"Error(text='{self._text}', error_code={self.error_code}"


def new_error(text: str, logger: logging.Logger = None, level: int = logging.ERROR, error_code: int = -1) -> _Error:
    err = _Error(text, error_code)
    if logger:
        logger.log(level, str(err))
    return err


error = Optional[_Error]
