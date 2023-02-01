"""Some types and constants."""
# pylint: disable=too-few-public-methods
NS = "starters"


class Status:
    """Pseudo-enum for managing statuses."""

    # the starter isn't done yet, and more data is required
    CONTINUING = "continuing"

    # the starter is done, and should not continue
    DONE = "done"

    # something terrible has happened
    ERROR = "error"
