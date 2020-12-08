from typing import Optional
import logging

__all__ = ["error", "new_error"]


class _Error:

    def __init__(self, text: str, error_code: int = -1):
        self._text = text
        self._error_code = error_code

    def __str__(self):
        return self._text

    def __repr__(self):
        return f"Error(text='{self._text}', error_code={self._error_code}"


def new_error(text: str, logger: logging.Logger = None, level: int = logging.ERROR) -> _Error:
    err = _Error(text, -1)
    if logger:
        logger.log(level, str(err))
    return err


error = Optional[_Error]
