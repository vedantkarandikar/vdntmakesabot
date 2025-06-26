from pydantic import BaseModel
from typing import Literal


class Variant(BaseModel):
    key: Literal[
        "standard",
        "chess960",
        "crazyhouse",
        "antichess",
        "atomic",
        "horde",
        "kingOfTheHill",
        "racingKings",
        "threeCheck",
        "fromPosition",
    ]
    name: str
    short: str
