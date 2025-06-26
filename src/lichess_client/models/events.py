from pydantic import BaseModel
from typing import Literal
from .game import GameEventInfo, GameStateEvent, GameFullEvent
from .challenge import ChallengeJson


class GameStartEvent(BaseModel):
    type: Literal["gameStart"]
    game: GameEventInfo


class ChallengeEvent(BaseModel):
    type: Literal["challenge"]
    challenge: ChallengeJson
