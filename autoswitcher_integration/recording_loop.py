"""
Idée : repartir du https://github.com/interactions-py/interactions.py/blob/5.x/interactions/api/voice/recorder.py
et créer une loop start/stop record qui a lieu d'écrire sur le disque, renvoie le byte array qu'on analyse. On garde en mémoire les n bytearrays précédents
puis on exécute le choix de la caméra basé sur les n bytes arrays précédents avec un score décroissant plus le byte array est vieux
On check les rôles > le rôle de l'utilisateur donne 
Dans les dernières fonctions >>> il y a la loop de recording ; l'adapter
"""

from select import select
from struct import pack
from collections import deque
from interactions.api.voice.audio import RawInputAudio


# loops between run and process_chunk

def run(self) -> None:

    sock = self.state.ws.socket
    readable, _, _ = select([sock], [], [], 0)
    while readable and sock.recv(4096):
        readable, _, _ = select([sock], [], [], 0)

    with self.audio:
        while self.recording:
            ready, _, err = select.select([sock], [], [sock], 0.01)
            if not ready:
                if err:
                    pass
                continue

            data = sock.recv(4096)

            if 200 <= data[1] <= 204:
                continue

            try:
                # loop de traitement ici
                raw_audio = RawInputAudio(self, data)
                process_chunk(raw_audio)
            except Exception as ex:
                pass

def process_chunk(self, raw_audio: RawInputAudio) -> None:
        """
        TODO : estimer si l'utilisateur est en train de parler ou non.
        Si ce n'est pas le cas, ajouter un poids de 0 à son array ; autrement, ajouter un poids positif.
        """
        if raw_audio.user_id is None:
            return

        if self.recording_whitelist and raw_audio.user_id not in self.recording_whitelist:
            return

        decoder = self.get_decoder(raw_audio.ssrc)

        if raw_audio.ssrc not in self.user_timestamps:
            if last_timestamp := self.audio.last_timestamps.get(raw_audio.user_id, None):
                diff = raw_audio.timestamp - last_timestamp
                silence = int(diff * decoder.sample_rate)

            else:
                silence = 0

            self.user_timestamps.update({raw_audio.ssrc: raw_audio.timestamp})
        else:
            silence = raw_audio.timestamp - self.user_timestamps[raw_audio.ssrc]
            if silence < 0.1:
                silence = 0
            self.user_timestamps[raw_audio.ssrc] = raw_audio.timestamp

        raw_audio.pcm = pack("<h", 0) * int(silence * decoder.sample_rate) * 2 + raw_audio.decoded

        # on ne cherche pas à write l'audio mais uniquement à l'analyser => le stocker dans un array global
        self.audio.write(raw_audio, raw_audio.user_id)

def select_speaker(buffer:dict[str,deque]) -> str:
    """
    Etant donné un dictionnaire contenant le nom des personnes sur le vocal
    ainsi que le level sonore au cours des n derniers intervalles de temps
    choisit l'utilisateur le plus actif avec pondération sur les dernières secondes.
    On utilisera une deque car quand on updatera le buffer
    il faudra pop un des bouts (début) et rajouter à l'autre (fin).
    """
    return list(
            buffer.keys()
        )[
            (
                scores := [
                        sum(
                            [score*i for i,score in enumerate(bf)]
                        ) for bf in list(buffer.values())
                        ]
                    ).index(
                max(scores)
            )
        ]