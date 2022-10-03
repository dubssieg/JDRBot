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


@timeout(8)
async def obs_invoke(f, *args) -> None:
    "appel avec unpacking via l'étoile"

    try:
        ws = obsws(args[0], args[1], args[2])
        ws.connect()
        await f(ws, args[3:])  # exécution de la fonction
        ws.disconnect()
    except:
        pass


async def toggle_anim(ws, name) -> None:
    try:
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=True))
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=False))
    except:
        pass
