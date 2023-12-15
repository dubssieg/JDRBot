from json import load
from random import choice, choices
#from pandas import read_csv

data_directory: str = "data/"
#reference_dataset = read_csv(f"{data_directory}dataset.csv")


def unpack_char(current_properties: dict, char: dict) -> dict:
    """Récupère les caractéristiques d'un attribut de personnage depuis un dictionnaire
    Agrège par probabilité... et récupère la bonne valeur

    Args:
        char (dict): un dico issu d'une liste de dict dans un json chargé
        current_properties (dict): propriétés déjà établies du personnage

    Returns:
        dictionnaire modifié par l'ajout de la nouvelle clé-valeur
    """
    try:
        if 'proba' in char:
            value = choices(char['values'], k=1, weights=char['proba'])[0]
        else:
            value = choice(char['values'])
    except:
        value = char['default']
    return {**current_properties, **{char['char_name']: value}}


def name() -> str:
    """Génère un nom de personnage

    Returns:
        str: nom du personnage
    """
    particles: dict = load(open(f'{data_directory}names.json', 'r'))
    debut, fin, mid1, mid2 = choice(particles["debut"]), choice(
        particles["fin"]), choice(particles["mid"]), choice(particles["mid"])
    return choice([f"{debut}{mid1}{mid2}{fin}", f"{debut}{mid1}{fin}", f"{debut}{fin}"])


def create_char(ethny: str) -> dict:
    character: dict = {'Nom': name()}
    property_set: list = load(open(f'{data_directory}{ethny}.json', 'r'))
    for char in property_set:
        character = unpack_char(character, char)
    return character


def get_personnas() -> dict:
    return load(open(f'{data_directory}descriptors.json', 'r'))
