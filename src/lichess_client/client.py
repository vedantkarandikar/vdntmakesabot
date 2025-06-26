import requests
import json
from typing import Generator, Union, Optional
from pydantic import ValidationError

from lichess_client.models.challenge import OkResponse
from lichess_client.models.events import ChallengeEvent, GameStartEvent
from lichess_client.models.game import GameFullEvent, GameStateEvent

NDJSON_EVENT = Union[GameStartEvent, ChallengeEvent]
NDJSON_GAME_EVENT = Union[GameFullEvent, GameStateEvent]


class LichessBotClient:
    BASE_URL = "https://lichess.org"

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/x-ndjson"}
        )

    # def _parse_ndjson_line(
    #     self, line: bytes
    # ) -> Optional[Union[NDJSON_EVENT, NDJSON_GAME_EVENT]]:
    #     try:
    #         data = json.loads(line)
    #         if data.get("type") == "gameStart":
    #             return GameStartEvent.model_validate(data)
    #         elif data.get("type") == "challenge":
    #             return ChallengeEvent.model_validate(data)
    #         elif data.get("type") == "gameFull":
    #             return GameFullEvent.model_validate(data)
    #         elif data.get("type") == "gameState":
    #             return GameStateEvent.model_validate(data)
    #     except (ValidationError, json.JSONDecodeError):
    #         pass
    #     return None

    def get_event_stream(self) -> requests.Response:
        url = f"{self.BASE_URL}/api/stream/event"
        resp = self.session.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp

    def _parse_ndjson_line(
        self, line: bytes
    ) -> Optional[Union[NDJSON_EVENT, NDJSON_GAME_EVENT]]:
        try:
            data = json.loads(line.decode("utf-8"))
            match data.get("type"):
                case "challenge":
                    return ChallengeEvent.model_validate(data)
                case "gameStart":
                    return GameStartEvent.model_validate(data)
                case "gameFull":
                    return GameFullEvent.model_validate(data)
                case "gameState":
                    return GameStateEvent.model_validate(data)
        except Exception as e:
            print("Failed to parse line:", e)
            print("Raw line:", line.decode("utf-8"))
        return None

    def stream_events(self) -> Generator[NDJSON_EVENT, None, None]:
        with self.get_event_stream() as resp:
            for line in resp.iter_lines():
                if line:
                    event = self._parse_ndjson_line(line)
                    if event:
                        yield event  # type: ignore

    # def stream_events(self) -> Generator[NDJSON_EVENT, None, None]:
    #     url = f"{self.BASE_URL}/api/stream/event"
    #     with self.session.get(url, stream=True) as resp:
    #         resp.raise_for_status()
    #         for line in resp.iter_lines():
    #             if line:
    #                 event = self._parse_ndjson_line(line)
    #                 if event:
    #                     yield event

    def get_game_stream(self, game_id: str) -> requests.Response:
        url = f"{self.BASE_URL}/api/bot/game/stream/{game_id}"
        resp = self.session.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp

    def make_move(
        self, game_id: str, move: str, offering_draw: Optional[bool] = None
    ) -> OkResponse:
        url = f"{self.BASE_URL}/api/bot/game/{game_id}/move/{move}"
        params = {}
        if offering_draw is not None:
            params["offeringDraw"] = str(offering_draw).lower()

        resp = self.session.post(url, params=params)
        resp.raise_for_status()
        return OkResponse.model_validate(resp.json())

    def accept_challenge(self, challenge_id: str) -> OkResponse:
        url = f"{self.BASE_URL}/api/challenge/{challenge_id}/accept"
        resp = self.session.post(url)
        resp.raise_for_status()
        print(resp.json())
        return OkResponse.model_validate(resp.json())

    def decline_challenge(
        self, challenge_id: str, reason: Optional[str] = None
    ) -> OkResponse:
        url = f"{self.BASE_URL}/api/challenge/{challenge_id}/decline"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"reason": reason} if reason else {}
        resp = self.session.post(url, headers=headers, data=data)
        resp.raise_for_status()
        return OkResponse.model_validate(resp.json())
