""" initial schema
"""
from pathlib import Path

from ..json_ import json_validator, loads

VERSION = "2"

HERE = Path(__file__).parent

SCHEMA = loads((HERE / f"v{VERSION}.json").read_text())
ALL_STARTERS = json_validator(SCHEMA)

_STARTER = dict(SCHEMA)
_STARTER["anyOf"] = [{"$ref": "#/definitions/starter"}]

STARTER = json_validator(_STARTER)

_STARTERS = dict(SCHEMA)
_STARTERS["anyOf"] = [{"$ref": "#/definitions/starters"}]
STARTERS = json_validator(_STARTERS)
