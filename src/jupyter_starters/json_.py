"""Some third-party preferred alternatives to stdlib/status quo for parsing and
validating JSON."""
# pylint: disable=invalid-name,c-extension-no-member
from typing import Any, Callable, Dict, Text

try:
    import ujson

    loads = ujson.loads
    dumps = ujson.dumps
except ImportError:  # pragma: no cover
    import json

    loads = json.loads  # type: ignore
    dumps = json.dumps  # type: ignore

try:
    import fastjsonschema.compile as json_validator
    from fastjsonschema import JsonSchemaException
except ImportError:
    from jsonschema import validate
    from jsonschema.exceptions import ValidationError as JsonSchemaException
    from jsonschema.validators import validator_for

    def json_validator(schema: Dict[Text, Any]) -> Callable[[Dict[Text, Any]], Any]:
        """Implements that fastjsonschema.compile API with jsonschema."""
        validator_cls = validator_for(schema)

        def _validate(instance: Dict[Text, Any]) -> Any:
            validate(instance, schema, cls=validator_cls)
            return instance

        return _validate


__all__ = ["loads", "dumps", "json_validator", "JsonSchemaException"]
