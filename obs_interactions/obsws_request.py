"Script to invoke animations in OBS Studio"
from typing import Callable
from asyncio import sleep as async_sleep
from obswebsocket import obsws, requests, exceptions
from platform import system as exploitation_os
from websocket import WebSocket


def host_up(host: str) -> bool:
    "Checks if OBS Websocket is available"
    try:
        toy_websocket: WebSocket = WebSocket()
        toy_websocket.connect(host)
        toy_websocket.close()
    except Exception:
        return False
    return True


async def obs_invoke(func: Callable, *args) -> None:
    """Calls a function to interact with socket
    Aims to check if connexion is possible

    Args:
        f (Callable): a function to execute, followed by its args
    """
    if host_up(f"ws://{args[0]}:{args[1]}"):
        websocket: obsws = obsws(args[0], args[1], args[2], timeout=5)
        try:
            websocket.connect()
            await func(websocket, *args[3:])  # exécution de la fonction
            websocket.disconnect()
        except exceptions.ConnectionFailure:
            print("OBS connexion failure.")
            return
        except exceptions.MessageTimeout:
            print("Timed out!")
            return
        except exceptions.ObjectError:
            print("OBS object error")
            return
    else:
        print("Impossible to connect, OBS Studio is not up.")
        return


async def toggle_anim(
        websocket: obsws,
        name: str,
        scene: str = "Animations",
        delay: int = 5
) -> None:
    """Toggle anim on, plays it, and toggles it off after a delay.

    Args:
        ws (obsws): A connected websocket
        name (str): Name of source
        scene (str, optional): A scene where the source is. Defaults to "Animations".
        delay (int, optional): Delay after which source should be toggled off. Defaults to 5.
    """
    websocket.call(requests.SetSceneItemProperties(
        scene_name=scene, item=name, visible=True))
    await async_sleep(delay)
    websocket.call(requests.SetSceneItemProperties(
        scene_name=scene, item=name, visible=False))


async def toggle_filter(
        websocket: obsws,
        name: str,
        filter_name: list[str],
        visibility: bool
) -> None:
    """Toggle filter on or off.

    Args:
        ws (obsws): A connected websocket
        name (str): Name of source to apply filter
        filter_name (list[str]): The list of filters to toggle
        visibility (bool): If should be visible or not
    """
    for elt in filter_name:
        websocket.call(requests.SetSourceFilterVisibility(
            sourceName=name, filterEnabled=visibility, filterName=elt))
