from enum import Enum
from pydantic import BaseModel


class GameColor(str, Enum):
    white = "white"
    black = "black"


class Speed(str, Enum):
    bullet = "bullet"
    blitz = "blitz"
    rapid = "rapid"
    classical = "classical"
    correspondence = "correspondence"
