from obswebsocket import obsws, requests
from os import path
from obswebsocket.exceptions import ConnectionFailure
from websocket._exceptions import WebSocketConnectionClosedException


def switch(creditentials: dict, requested_name: str) -> None:
    ws = obsws(creditentials["host"],
               creditentials["port"], creditentials["password"])
    try:
        ws.connect()
        ws.call(requests.SetCurrentScene(requested_name))
    except KeyboardInterrupt:
        ws.disconnect()
        print("Connexion closed!")
    except ConnectionFailure:
        print(
            "Could not connect to OBS ; please check creditentials file and if OBS is up and running.")
    except WebSocketConnectionClosedException:
        print("Connexion to OBS was prematurely closed ; aborting...")
    except ConnectionRefusedError:
        print("OBS refused connexion to the switcher.")


def get_scene_list(creditentials: dict) -> list:
    ws = obsws(creditentials["host"],
               creditentials["port"], creditentials["password"])
    try:
        ws.connect()
        return [scene['name'] for scene in ws.call(requests.GetSceneList()).getScenes()]
    except KeyboardInterrupt:
        ws.disconnect()
        print("Connexion closed!")
    except ConnectionFailure:
        print(
            "Could not connect to OBS ; please check creditentials file and if OBS is up and running.")
    except WebSocketConnectionClosedException:
        print("Connexion to OBS was prematurely closed ; aborting...")
    except ConnectionRefusedError:
        print("OBS refused connexion to the switcher.")
