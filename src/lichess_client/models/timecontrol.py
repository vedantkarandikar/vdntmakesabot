from pydantic import BaseModel
from typing import Literal


class TimeControl(BaseModel):
    type: Literal["clock"]
    limit: int
    increment: int
    show: str
