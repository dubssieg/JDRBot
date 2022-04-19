from json import load, dump


def load_json(json_file: str) -> dict:
    """
    Charge un fichier json en un dictionnaire
    * json_file (str) : le chemin d'accès au fichier
    """
    return load(open(f"env/{json_file}.json", "r"))


def save_json(json_file: str, dico_save: dict) -> None:
    """
    Sauve un dictionnaire en un fichier json
    * json_file (str) : le chemin d'accès au fichier
    * dico_save (dict) : le dictionnaire à sauvegarder
    """
    dump(dico_save, open(f"env/{json_file}.json", "w"))


def init():
    """
    Initialise les dicos d'environnement pour la première exécution
    """

    dict_stats: dict = {
        '!par': 'Parade',
        '!res': 'Résistance',
        '!cou': 'Course',
        '!abs': 'Abstraction',
        '!mag': 'Magie',
        '!con': 'Connaissance',
        '!pou': 'Pousser',
        '!sur': 'Survie',
        '!fra': 'Frappe',
        '!dec': 'Déchiffrement',
        '!obs': 'Observation',
        '!ref': 'Réflexion',
        '!esq': 'Esquive',
        '!fur': 'Furtivité',
        '!pre': 'Précision',
        '!art': 'Arts et culture',
        '!emp': 'Empathie',
        '!cha': 'Charme et influence'
    }

    dict_pos: dict = {
        'Parade': 'E12',
        'Résistance': 'E13',
        'Course': 'E14',
        'Abstraction': 'E15',
        'Magie': 'E16',
        'Connaissance': 'E17',
        'Pousser': 'E18',
        'Survie': 'E19',
        'Frappe': 'E20',
        'Déchiffrement': 'E21',
        'Observation': 'E22',
        'Réflexion': 'E23',
        'Esquive': 'E24',
        'Furtivité': 'E25',
        'Précision': 'E26',
        'Arts et culture': 'E27',
        'Empathie': 'E28',
        'Charme et influence': 'E29',
        'Stress': 'G31'
    }

    dict_links: dict = {}

    dict_stress: dict = {
        "Acte de bravoure 3": "Si en combat, vous agissez et vous gagnez 3 points dans une statistique mentale. Si hors combat, chaque membre gagne 3 points dans une statistique mentale.",
        "Espoir renaissant 3": "3 personnages-joueurs peuvent décaler leur cadre de lecture de stress de 1.",
        "Acte de bravoure 2": "Si en combat, vous agissez et vous gagnez 2 points dans une statistique mentale. Si hors combat, chaque membre gagne 2 points dans une statistique mentale.",
        "Espoir renaissant 2": "2 personnages-joueurs peuvent décaler leur cadre de lecture de stress de 1.",
        "Focus 3": "Si en combat, chaque membre gagne un bonus de 3 pour sa prochaine action. Si hors combat, vous gagnez les effets d’un test d’observation réussi critiquement.",
        "Acte de bravoure 1": "Si en combat, vous agissez et vous gagnez 1 point dans une statistique mentale. Si hors combat, chaque membre gagne 1 point dans une statistique mentale.",
        "Focus 2": "Si en combat, chaque membre gagne un bonus de 2 pour sa prochaine action. Si hors combat, vous gagnez les effets d’un test d’observation réussi critiquement.",
        "Impassible 3": "Le personnage-joueur de votre choix a une action d’opportunité.",
        "Espoir renaissant 1": "1 personnage-joueur peut décaler son cadre de lecture de stress de 1.",
        "Impassible 2": "Un personnage-joueur aléatoire a une action d’opportunité.",
        "Humour noir 1": "Lancez un dé à deux faces. Pour un résultat de 0 ou 1, un allié avec lequel vous seriez susceptible d’interagir perd/gagne (respectivement) 1 point dans une statistique mentale.",
        "Focus 1": "Si en combat, chaque membre gagne un bonus de 1 pour sa prochaine action. Si hors combat, vous gagnez les effets d’un test d’observation réussi critiquement.",
        "Impassible 1": "Vous restez impassible.",
        "Humour noir 2": "Lancez un dé à deux faces. Pour un résultat de 0 ou 1, un allié avec lequel vous seriez susceptible d’interagir perd/gagne (respectivement) 2 points dans une statistique mentale.",
        "Paranoia 1": "Votre peur se propage à un allié, il lance un jet de stress.",
        "Humour noir 3": "Lancez un dé à deux faces. Pour un résultat de 0 ou 1, un allié avec lequel vous seriez susceptible d’interagir perd/gagne (respectivement) 3 points dans une statistique mentale.",
        "Terreur enfouie 1": "Le MJ prend le contrôle de votre personnage et peut effectuer jusqu’à 1 action, tant que celle-ci entre dans le cadre temporel d’un tour.",
        "Paranoia 2": "La cause de ce jet devient une nouvelle phobie, ou la renforce.",
        "Trahison 1": "L’allié que vous seriez susceptible d’attaquer lance un jet de stress.",
        "Terreur enfouie 2": "Le MJ prend le contrôle de votre personnage et peut effectuer jusqu’à 2 actions distinctes, tant que celles-ci entrent dans le cadre temporel d’un tour.",
        "Paroles du fou 1": "1 personnage-joueur décale son cadre de lecture de stress de 1 vers le bas.",
        "Paranoia 3": "La cause de ce jet devient une nouvelle phobie, ou la renforce pour vous et un allié.",
        "Trahison 2": "Vous attaquez instantanément l’allié qu’il vous est le plus aisé de toucher.",
        "Paroles du fou 2": "2 personnages-joueurs décalent leur cadre de lecture de stress de 1 vers le bas.",
        "Epreuve de foi 1": "Si en combat, votre corps va prendre le dessus (spasmes, nausées…), l’affliction sera faible. Si hors combat, vous allez succomber à la panique et vivre une crise d’angoisse,la crise étant faible.",
        "Paroles du fou 3": "3 personnages-joueurs décalent leur cadre de lecture de stress de 1 vers le bas.",
        "Epreuve de foi 2": "Si en combat, votre corps va prendre le dessus (spasmes, nausées…), l’affliction sera modérée. Si hors combat, vous allez succomber à la panique et vivre une crise d’angoisse,la crise étant modérée.",
        "Terreur enfouie 3": "Le MJ prend le contrôle de votre personnage et peut effectuer jusqu’à 3 actions distinctes, tant que celles-ci entrent dans le cadre temporel d’un tour.",
        "Epreuve de foi 3": "Si en combat, votre corps va prendre le dessus (spasmes, nausées…), l’affliction sera extrème. Si hors combat, vous allez succomber à la panique et vivre une crise d’angoisse,la crise étant extrème.",
        "Trahison 3": "Vous attaquez instantanément l’allié qu’il vous est le plus aisé de toucher, et il lance un jet de stress."
    }

    save_json("stats", dict_stats)
    save_json("pos", dict_pos)
    save_json("links", dict_links)
    save_json("stress", dict_stress)


if __name__ == "__main__":
    init()
