

class InvalidData(Exception):
    """Schema validation errors will be caught by the API."""

    def __init__(self, errors):
        self.errors = errors
        super(InvalidData, self).__init__(repr(errors))


class InvalidModel(Exception):
    """The schema model is not defined correctly."""
    pass


class InvalidMapping(Exception):
    """A data mapping was invalid."""
    pass
