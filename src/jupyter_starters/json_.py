""" some third-party preferred alternatives to stdlib/status quo for parsing
    and validating JSON
"""
# pylint: disable=invalid-name,c-extension-no-member
from typing import Any, Callable, Dict, Text

try:
    import ujson

    loads = ujson.loads
    dumps = ujson.dumps
except ImportError:
    import json

    loads = json.loads
    dumps = json.dumps

try:
    import fastjsonschema.compile as json_validator
    from fastjsonschema import JsonSchemaException
except ImportError:
    from jsonschema import validate
    from jsonschema.validators import validator_for
    from jsonschema.exceptions import ValidationError as JsonSchemaException

    def json_validator(schema: Dict[Text, Any]) -> Callable[[Dict[Text, Any]], Any]:
        """implements that fastjsonschema.compile API with jsonschema"""
        validator_cls = validator_for(schema)

        def _validate(instance: Dict[Text, Any]) -> Any:
            validate(instance, schema, cls=validator_cls)
            return instance

        return _validate


__all__ = ["loads", "dumps", "json_validator", "JsonSchemaException"]
