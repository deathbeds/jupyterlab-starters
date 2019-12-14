""" initial schema
"""
from pathlib import Path

from .._json import json_validator, loads

HERE = Path(__file__).parent

SCHEMA = loads((HERE / "v1.json").read_text())
ALL_STARTERS = json_validator(SCHEMA)

_STARTER = dict(SCHEMA)
_STARTER["anyOf"] = [{"$ref": "#/definitions/starter"}]

STARTER = json_validator(_STARTER)

_STARTERS = dict(SCHEMA)
_STARTERS["anyOf"] = [{"$ref": "#/definitions/starters"}]
STARTERS = json_validator(_STARTERS)
