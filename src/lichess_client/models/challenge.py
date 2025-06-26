from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal
from .base import Speed, GameColor
from .variant import Variant
from .timecontrol import TimeControl


class ChallengeUser(BaseModel):
    id: str
    name: str
    rating: Optional[int]
    title: Optional[str]
    provisional: Optional[bool] = False
    online: Optional[bool] = True
    lag: Optional[int] = 0

    class Config:
        extra = "allow"


class ChallengeJson(BaseModel):
    id: str
    url: HttpUrl
    status: str
    challenger: ChallengeUser
    destUser: Optional[ChallengeUser]
    variant: Variant
    rated: bool
    speed: Speed
    timeControl: TimeControl
    color: Literal["white", "black", "random"]
    finalColor: Optional[GameColor]
    perf: dict
    direction: Optional[Literal["in", "out"]] = None
    initialFen: Optional[str] = None

    class Config:
        extra = "allow"


class OkResponse(BaseModel):
    ok: bool
