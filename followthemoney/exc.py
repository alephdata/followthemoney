from typing import Dict, Optional, TypedDict


class ErrorSpec(TypedDict, total=False):
    properties: Dict[str, str]


class FollowTheMoneyException(Exception):
    """Catch-all exception for errors emitted by this library."""

    pass


class InvalidData(FollowTheMoneyException):
    """Schema validation errors will be caught by the API."""

    def __init__(self, message: str, errors: Optional[ErrorSpec] = None) -> None:
        super(InvalidData, self).__init__(message)
        self.errors: ErrorSpec = errors or {}


class InvalidModel(FollowTheMoneyException):
    """The schema model is not defined correctly."""

    pass


class InvalidMapping(FollowTheMoneyException):
    """A data mapping was invalid."""

    pass
