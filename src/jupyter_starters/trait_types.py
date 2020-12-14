""" some more traits

    these are not typechecked yet, because of the impedance between traitlets,
    JSON Schema, and mypy.
"""

# pylint: disable=broad-except,unused-argument
import traitlets

from .json_ import JsonSchemaException


class Schema(traitlets.Any):
    """any... but validated by a :func:`jupyter_starters.json_.json_validator`"""

    _validator = None

    def __init__(self, validator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validator = validator

    def validate(self, obj, value):
        """applies a validator"""
        try:
            self._validator(value)
        except JsonSchemaException as err:
            raise traitlets.TraitError(f"""schema errors: {err}""")
        return value
