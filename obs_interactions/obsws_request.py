"Script to invoke animations in OBS Studio"
from typing import Callable
from asyncio import sleep as async_sleep
from obswebsocket import obsws, requests, exceptions
from websockets import connect, exceptions


async def obs_invoke(func: Callable, *args) -> None:
    """Calls a function to interact with socket
    Aims to check if connexion is possible

    Args:
        f (Callable): a function to execute, followed by its args
    """
    try:
        async with connect(uri=f"ws://{args[0]}:{args[1]}") as ws:
            await ws.send('ping')
            await ws.recv()

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

    except (RuntimeError, exceptions.ConnectionClosed) as e:
        print('Echec de la connexion au socket:', e.args)
        return
    except (exceptions.InvalidStatusCode, ConnectionResetError, exceptions.InvalidMessage, ConnectionRefusedError) as e:
        print('Echec de la connexion au socket:', e)
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
