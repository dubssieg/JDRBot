from lib import save_json


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
        'Stress': 'G31',
        'Héroisme': 'C32'
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

    dict_helps: dict = {
        "!support": "pour obtenir de l'aide",
        "!gennom": "pour générer un nom aléatoire",
        "!genpnj": "pour générer un PnJ aléatoire",
        "!linkjdr": "pour récupérer les liens utiles pour les séances",
        "!linkprojet": "pour obtenir les liens vers les projets",
        "!dX+Y/Z": "pour lancer un dé à X faces avec un bonus de Y sur une difficulté de Z",
        "!dX+Y": "pour lancer un dé à X faces avec un bonus de Y sans valeur de difficulté",
        "!sX": "pour lancer un dé de stress avec un stress de X",
        "!wpX+Y": "pour lancer un sondage sur X jours décalé de Y jours",
        "!toss": "pour lancer une pièce et obtenir pile ou face",
        "!savefile filename": "pour créer un lien symbolique entre votre ID discord et un nom de fiche",
        "!meow": "parce qu'il faut forcément un chat !"
    }

    embed_jdr: dict = {
        "Watch2Gether": ["Sert pour la musique pendant les séances", "https://w2g.tv/rooms/i0bpwst6mzv3t9qh9c7?access_key=vivvyyity2uburxwxo4wjm"],
        "Manuel des règles": ["Pour se mettre à jour sur le système", "https://decorous-ptarmigan-9bf.notion.site/R-gles-JdR-ddd3ac0d4d0c4f98a9b2bcdd0d5cda79"],
        "GDoc du lore": ["Pour se rafraîchir la mémoire sur le lore", "https://docs.google.com/document/d/1Ytnvfar50VX2DmUkk1DoovrHz-nE_BAlFBGAkjkNX3Y/edit?usp=sharing"],
        "Retours de séances": ["Faites vos retours ici après la fin d'une série de JdR !", "https://forms.gle/9nSjZwnFQChf9j546"]
    }

    embed_projets: dict = {
        "Youtube principal": ["Replays de JdR et chroniques rôlistes", "https://www.youtube.com/channel/UCCn873wDjYSl_YZpNNTbViA"],
        "Chaine de replays": ["Ce que vous n'avez pas vu en live", "https://www.youtube.com/channel/UCmmNBnYQmZlv6tPz6MO2TNA"],
        "Streams twitch": ["Où on a des concepts variés", "https://www.twitch.tv/tharostv"],
        "Github des projets": ["Nourri aux bons utilitaires pour du JdR", "https://github.com/Tharos-ux"],
        "Cycle de Niathshrubb": ["Pour découvrir ce que j'écris", "https://docs.google.com/document/d/1BC4PwwgtKJVfi3yFeJVzcIasZL3iVizx-WNH1jVvk9U/edit?usp=sharing"]
    }

    quotes: dict = {
        "ECHEC":
            [
                "Malheureuses circonstances ou compétences insuffisantes ? Seule la certitude de votre échec demeure.",
                "Qui n'avait point prévu ces remuantes choses dans l'ombre ?",
                "La vérité n'éclot jamais du mensonge.",
                "A espoirs illusoires, rêves déchus !"
            ],
        "ECHEC CRITIQUE":
            [
                "La chance ne vous sourit pas toujours... et ce revers de fortune est cruel !"
            ],
        "REUSSITE":
            [
                "Un coup décisif pour la chair comme pour l'esprit !",
                "La voie est claire, le chemin dégagé : ne nous manque plus que la force pour l'emprunter."
            ],
        "REUSSITE CRITIQUE":
            [
                "Brillant ! Que brûle la flamme, brasier de peur en vos ennemis !"
            ],
        "INCONNU":
            [
                "Une progression n'est pas toujours linéaire...",
                "Le pire reste de ne pas savoir que l'on ne sait pas.",
                "L'inconnu, fantasme des savants, plaie des vivants !"
            ],
        "STRESS POSITIF":
            [
                "C'est quand tout semble perdu que l'esprit est à son plus fort !",
                "De l'espoir, là même où les plus fous n'auraient su en trouver."
            ],
        "STRESS NEGATIF":
            [
                "Les ténèbres les plus profondes sont bien souvent celles de notre esprit...",
                "La vie n'est que coups au coeur et à l'esprit."
            ],
        "STRESS NEUTRE":
            [
                "Maladies de l'esprit sont peste pour la chair !",
                "Pouce par pouce, une seule vérité s'impose à vous : celle du tombeau.",
                "A quoi bon frapper un mal que l'on ne saurait voir ?"
            ]
    }

    # saving all files
    save_json("stats", dict_stats)
    save_json("pos", dict_pos)
    save_json("links", dict_links)
    save_json("stress", dict_stress)
    save_json("helps", dict_helps)
    save_json("embed_jdr", embed_jdr)
    save_json("embed_projets", embed_projets)
    save_json("quotes", quotes)


if __name__ == "__main__":
    init()
