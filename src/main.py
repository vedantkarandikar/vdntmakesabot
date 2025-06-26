# File: src/bot.py
import os
import threading
from lichess_client.client import LichessBotClient
from lichess_client.models.events import ChallengeEvent, GameStartEvent
from game_handler import GameHandler
from engine import MyEngine


def main():
    token = os.environ["LICHESS_TOKEN"]
    lichess = LichessBotClient(token)
    print("Listening for events...")

    engine = MyEngine()
    handler = GameHandler(lichess, engine)

    for event in lichess.stream_events():
        print("Got event:", event)

        if isinstance(event, ChallengeEvent):
            challenge = event.challenge
            if challenge.variant.key != "standard":
                print(f"Declining challenge {challenge.id} (non-standard)")
                lichess.decline_challenge(challenge.id, reason="standard")
                continue

            print(f"Accepting challenge {challenge.id}")
            lichess.accept_challenge(challenge.id)

        elif isinstance(event, GameStartEvent):
            game_id = event.game.gameId
            print(f"Starting game {game_id}")
            threading.Thread(
                target=handler.handle_game, args=(game_id,), daemon=True
            ).start()


if __name__ == "__main__":
    main()
