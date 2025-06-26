from pydantic import BaseModel
from typing import Literal, Optional
from .base import GameColor, Speed


class GameEventOpponent(BaseModel):
    id: Optional[str]
    username: Optional[str]


class GameCompat(BaseModel):
    bot: Optional[bool]


class GameEventInfo(BaseModel):
    fullId: str
    gameId: str
    color: GameColor
    lastMove: Optional[str]
    speed: Optional[Speed]
    rated: Optional[bool]
    opponent: Optional[GameEventOpponent]
    isMyTurn: Optional[bool]
    secondsLeft: Optional[int]
    compat: Optional[GameCompat]


class GameStateEvent(BaseModel):
    type: Literal["gameState"]
    moves: str
    wtime: int
    btime: int
    winc: int
    binc: int
    status: str  # Accepting as str instead of Enum for flexibility
    winner: Optional[GameColor] = None  # ✅ Add = None here


class GameFullEvent(BaseModel):
    type: Literal["gameFull"]
    id: str
    speed: Speed
    rated: bool
    white: dict
    black: dict
    initialFen: str
    state: GameStateEvent
