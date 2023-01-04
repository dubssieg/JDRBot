from obswebsocket import obsws, requests
from os import path
from obswebsocket.exceptions import ConnectionFailure
from websocket._exceptions import WebSocketConnectionClosedException
from requests import get
from urllib.parse import urlencode
from time import sleep

SCENES_WHERE_SHOWING: list = ["Discussion_Solo",
                              "Presentation", "Dual", "Fullscreen", "Rolls_Solo_Tharos", "Rolls_Solo_Yoka", "Rolls_Solo_Invité_1", "Rolls_Solo_Invité_2", "Main_Pause_Rolls"]
NAME_OF_EMBED_SCENE: str = "Embed"
NAME_OF_BROWSER_SOURCE: str = "twitter_embed"
X_IN_SCENE: int = 1580
X_OUT_OF_BOUNDS: int = 2000
Y_POS: int = 150


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
