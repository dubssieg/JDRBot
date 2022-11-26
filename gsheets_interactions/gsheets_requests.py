

################ Commandes GSHEETS #################


def googleask(func):
    "Décorateur. Gère si l'utilisateur a bien une fiche à son nom"
    def wrapper(*args, **kwargs):
        if args[0] in args[1]:
            try:
                return func(*args, **kwargs)
            except:
                raise ConnectionError()
        else:
            raise ValueError()
    return wrapper


@googleask
def increase_on_crit(name: str, dict_links: dict, gc, stat: str,  dict_pos: str, valeur=1) -> None:
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
def get_stress(name: str, dict_links: dict, gc) -> str:
    """
    Renvoie la valeur de stress pour le jet de dés
    * name (str) : nom du joueur
    """
    return gc.open(dict_links[f"{name}"])[0].cell('G31').value


@googleask
def stat_from_player(name: str, dict_links: dict, gc, stat: str) -> str:
    return {e[0].value: e[1].value + e[2].value for e in gc.open(dict_links[f"{name}"])[0].range('C12:E29')}[stat]
