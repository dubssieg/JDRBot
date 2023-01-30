"""
        ################ Commandes GSHEETS #################

Toutes les commandes doivent avoir les trois mêmes premières variables :

    Args:
        name (str): nom de la personne qui a demandé une valeur
        dict_links (dict): liens entre fiches et personnes
        gc : connection

        qui doivent être renseignées DANS CET ORDRE (pour le décorateur)
"""


def googleask(func):
    "Décorateur. Gère si l'utilisateur a bien une fiche à son nom"
    def wrapper(*args, **kwargs):
        if args[0] in args[1]:
            try:
                return func(*args, **kwargs)
            except (ConnectionError, ValueError, KeyError):
                print(ConnectionError(
                    "Impossible to connect to the specified sheet."))
        else:
            print(ValueError("Impossible to get the required value."))
    return wrapper


@googleask
def increase_on_crit(name: str, dict_links: dict, gc, stat: str,  dict_pos: dict, valeur=1) -> None:
    """
    Update la valeur de stat en cas de critique
    * stat (str) : stat à modifier
    * name (str) : nom du joueur chez qui chercher la fiche
    * valeur (int - def. 1) : l'incrément à apposer à la stat
    """
    cellule = dict_pos[stat]
    sh = gc.open(dict_links[f"{name}"])
    wks = sh[0]
    value = int(wks.cell(cellule).value)
    wks.update_value(cellule, value+valeur)


@googleask
def hero_point_update(name: str, dict_links: dict, gc, checking: bool) -> bool:
    """Gère l'usage de points d'héroïsme

    Args:
        name (str): nom de la personne qui a demandé une valeur
        dict_links (dict): liens entre fiches et personnes
        gc : connection
        checking (bool): si on cherche à update la fiche de la personne ou non

    Returns:
        bool: si le point d'héroïsme a été utilisé par l'action
    """
    if checking:
        cellule: str = 'C32'
        sheet = gc.open(dict_links[f"{name}"])
        wks = sheet[0]
        value = int(wks.cell(cellule).value)
        if value > 0:
            wks.update_value(cellule, value-1)
            return True
        return False
    return False


@googleask
def get_stress(name: str, dict_links: dict, gc) -> str:
    """
    Renvoie la valeur de stress pour le jet de dés
    * name (str) : nom du joueur
    """
    return gc.open(dict_links[f"{name}"])[0].cell('G31').value


@googleask
def stat_from_player(name: str, dict_links: dict, gc, stat: str) -> str:
    """Récupère la valeur de lancer de dé d'un joueur.

    Args:
        name (str): nom de la personne qui a demandé une valeur
        dict_links (dict): liens entre fiches et personnes
        gc : connection
        stat (str): la stat demandée pour le jet

    Returns:
        str: valeur du dé à lancer avec la valeur bonus de compétence
    """
    return {
        e[0].value: e[1].value + e[3].value
        for e in gc.open(dict_links[f"{name}"])[0].range('B12:E29')
    }[stat]


@googleask
def values_from_player(name: str, dict_links: dict, gc) -> dict:
    """Récupère des valeurs de caractéristiques

    Args:
        name (str): nom de la personne qui a demandé une valeur
        dict_links (dict): liens entre fiches et personnes
        gc : connection

    Returns:
        dict: _description_
    """
    return {
        e[0].value:
            {'valeur_max': int(e[3].value), 'seuil_critique': int(
                e[4].value), 'valeur_actuelle': int(e[5].value)}
            for e in gc.open(dict_links[f"{name}"])[0].range('A3:F8')
    }


@googleask
def update_char(name: str, dict_links: dict, gc, competence_pos: dict,
                nom_competence: str, nouvelle_valeur: int):
    """Met à jour une caractéristique

    Args:
        name (str): nom de la personne qui a demandé une valeur
        dict_links (dict): liens entre fiches et personnes
        gc : connexion
        competence_pos (dict): description des positions des compétences sur la feuille
        nom_competence (str): nom de compétence à mettre à jour
        nouvelle_valeur (int): valeur à placer dans la case correspondante
    """
    cellule = competence_pos[nom_competence]
    sh = gc.open(dict_links[f"{name}"])
    wks = sh[0]
    wks.update_value(cellule, nouvelle_valeur)
