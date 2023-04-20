"Script to invoke anims in OBS Studio"
import signal
import asyncio
from obswebsocket import obsws, requests


def timeout(seconds_before_timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimeoutError(f"Error at {signum} for {frame} !")

        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds_before_timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        new_f.__name__ = f.__name__
        return new_f
    return decorate


# @timeout(8)
async def obs_invoke(f, *args) -> None:
    "appel avec unpacking via l'étoile"

    ws = obsws(args[0], args[1], args[2], timeout=10)
    try:
        ws.connect()
    except:
        return
    await f(ws, *args[3:])  # exécution de la fonction
    ws.disconnect()


async def toggle_anim(ws, name) -> None:
    "toggle anim on, plays it, and toggles it off."
    try:
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name, visible=True))
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name, visible=False))
    except Exception as exc:
        print(exc)


async def toggle_filter(ws, name, filter_name, visibility) -> None:
    "toggle filter on or off."
    try:
        for elt in filter_name:
            ws.call(requests.SetSourceFilterVisibility(
                sourceName=name, filterEnabled=visibility, filterName=elt))
    except Exception as exc:
        print(exc)
