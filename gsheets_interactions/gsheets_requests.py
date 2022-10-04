

################ Commandes GSHEETS #################


def stat_from_player(gc, stat, joueur, dict_links):
    stats = get_stats(joueur)
    if stats != None:
        return get_stats(gc, joueur, dict_links)[stat]
    return None


def googleask(func):
    "Décorateur. Gère si l'utilisateur a bien une fiche à son nom"
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return wrapper


@googleask
def increase_on_crit(gc, stat: str, name: str, dict_pos: str, dict_links: dict, valeur=1):
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
def hero_point_update(gc, name: str, checking: bool, dict_links: dict) -> bool:
    """
    Update la valeur de stat en cas de critique
    * stat (str) : stat à modifier
    * name (str) : nom du joueur chez qui chercher la fiche
    * valeur (int - def. 1) : l'incrément à apposer à la stat
    """
    if checking:
        cellule: str = 'C32'
        sh = gc.open(dict_links[f"{name}"])
        wks = sh[0]
        value = int(wks.cell(cellule).value)
        if value > 0:
            wks.update_value(cellule, value-1)
            return True
        return False
    return False


@googleask
def get_stress(gc, name: str, dict_links: dict):
    """
    Renvoie la valeur de stress pour le jet de dés
    * name (str) : nom du joueur
    """
    return gc.open(dict_links[f"{name}"])[0].cell('G31').value


@googleask
def get_stats(gc, name: str, dict_links: dict) -> dict:
    """
    Renvoie un dictionnaire de stats
    *name (str) : nom du joueur
    """
    # connexion
    sh = gc.open(dict_links[f"{name}"])
    wks = sh[0]
    # récupération des cellules d'intérêt
    cell_list = wks.range('C12:E29')
    d = dict()
    for e in cell_list:
        d[e[0].value] = e[1].value + e[2].value
    return d
