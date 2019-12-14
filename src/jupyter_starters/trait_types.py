""" some more traits
"""
# pylint: disable=broad-except,unused-argument
import six
import traitlets

from ._json import JsonSchemaException


class Schema(traitlets.Any):
    """ any... but validated by a jsonschema.Validator
    """

    _validator = None

    def __init__(self, validator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validator = validator

    def validate(self, obj, value):
        """ applies a validator
        """
        try:
            self._validator(value)
        except JsonSchemaException as err:
            raise traitlets.TraitError(f"""schema errors: {err}""")
        return value


class LoadableCallable(traitlets.TraitType):
    """A trait which (maybe) loads a callable."""

    info_text = "a loadable callable"

    def validate(self, obj, value):
        """ is it loadable? can it be made callable?
        """
        if isinstance(value, str):
            try:
                value = traitlets.import_item(value)
            except Exception:
                self.error(obj, value)

        if six.callable(value):
            return value

        self.error(obj, value)
        return None
