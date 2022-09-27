import argparse
import asyncio
from obswebsocket import obsws, requests
from lib import output_msg
import signal
from contextlib import contextmanager


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


async def obs_invoke(f, *args) -> None:
    "appel avec unpacking via l'étoile"

    host = "192.168.1.36"
    port = 4444
    password = "duboisie97"

    ws = obsws(host, port, password)
    try:
        ws.connect()
        await f(ws, args)  # exécution de la fonction
        ws.disconnect()
    except Exception:
        output_msg("Impossible de se connecter à OBS Studio.")


async def toggle_anim(ws, name) -> None:
    try:
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=True))
        output_msg(f"L'animation {name} est lancée !")
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=False))

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # declaring args
    parser.add_argument(
        "anim", help="animation a lancer", type=str)
    # executing args
    args = parser.parse_args()

    try:
        with time_limit(10):
            future = obs_invoke(toggle_anim, args.anim)
    except TimeoutException as e:
        print("Timed out!")
