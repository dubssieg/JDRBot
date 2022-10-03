from re import S
import interactions
import discord
import datetime
import asyncio
import signal

from random import randrange, random, choice
from lib import load_json, save_json
from pygsheets import authorize
from string import ascii_uppercase
from obswebsocket import obsws, requests

#############################
### Chargement des tokens ###
#############################

# tokens OBS-WS
tokens_obsws: dict = load_json("obs_ws")
host: str = tokens_obsws["host"]
port: int = tokens_obsws["port"]
password: str = tokens_obsws["password"]

# tokens discord
tokens_connexion: dict = load_json("token")
token_grifouille: str = tokens_connexion['token']
guild_id: int = tokens_connexion['guild_id']

bot = interactions.Client(
    token=token_grifouille)

# tokens GSheets
gc = authorize(service_file='env/connectsheets-341012-fddaa9df86d9.json')


# datas d'environnement
dict_stats: dict = load_json("stats")
dict_pos: dict = load_json("pos")
dict_links: dict = load_json("links")
dict_stress: dict = load_json("stress")

embed_projets: dict = load_json("embed_projets")
embed_jdr: dict = load_json("embed_jdr")
quotes: dict = load_json("quotes")

# préparation du dico de stress

listStates = [key for key in dict_stress.keys()]
listEffects = [value for value in dict_stress.values()]

# listes utiles à déclarer en amont
list_letters: list = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9", "\U0001F1EA", "\U0001F1EB", "\U0001F1EC", "\U0001F1ED",
                      "\U0001F1EE", "\U0001F1EF", "\U0001F1F0", "\U0001F1F1", "\U0001F1F2", "\U0001F1F3", "\U0001F1F4", "\U0001F1F5", "\U0001F1F6", "\U0001F1F7"]
descs_jdr: list = ["Liens utiles aux JdR", "Retrouvez ici tous les liens pouvant vous servir durant les séances, n'oubliez pas non plus d'ouvrir votre petite fiche de personnage !",
                   "En espérant que cela vous ait été utile !"]
descs_projets: list = ["Liens vers mes projets", "Retrouvez tous les liens vers les projets ici ; tout n'est pas directement en lien avec le JdR mais parfois plus largement avec mes projets !",
                       "Merci pour tous vos partages et vos retours, c'est adorable !"]
list_days: list = ["Lundi", "Mardi", "Mercredi",
                   "Jeudi", "Vendredi", "Samedi", "Dimanche"]

stats_choices: list = [interactions.Choice(
    name=val, value=val) for val in dict_stats.values()]

################ Pour demander la fiche #################


@bot.command(
    name="save_file",
    description="Sauvegarde un lien avec une fiche de statisitiques",
    scope=guild_id,
)
async def save_file(ctx):
    modal = interactions.Modal(
        title="Lier une feuille de stats",
        custom_id="mod_app_form",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Entrez le nom de votre fiche sur GoogleSheets",
                custom_id="text_input_response",
                min_length=1,
                max_length=20,
            )
        ],
    )
    await ctx.popup(modal)


@bot.modal("mod_app_form")
async def modal_response(ctx, response: str):
    dict_links[f"{ctx.author.mention}"] = f"{response}"
    save_json('links', dict_links)
    await ctx.send(f"La fiche nommée {response} vous a été liée !", ephemeral=True)

################ OBS Websocket functions #################


def timeout(seconds_before_timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimeoutError()

        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds_before_timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        new_f.__name__ = f.__name__
        return new_f
    return decorate


@timeout(8)
async def obs_invoke(f, *args) -> None:
    "appel avec unpacking via l'étoile"

    try:
        ws = obsws(host, port, password)
        ws.connect()
        await f(ws, args)  # exécution de la fonction
        ws.disconnect()
    except:
        pass


async def toggle_anim(ws, name) -> None:
    try:
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=True))
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=False))
    except:
        pass


################ Pour faire un weekpoll ############

"""
@bot.command(
    name="weekpoll",
    description="Effectue un sondage de dates pour trouver une correspondance",
    scope=guild_id,
)
async def weekpoll(ctx):
    modal = interactions.Modal(
        title="Assistant de calendrirer",
        custom_id="calendar_form",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Entrez le titre du sondage",
                custom_id="title",
                min_length=1,
                max_length=30,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Entrez la date de début (format jj/mm/aaaa)",
                custom_id="start",
                min_length=10,
                max_length=10,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Nombre de jours sur lequel se déroule le sondage (max. 18)",
                custom_id="duration",
                min_length=1,
                max_length=2,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Entrez le sous-texte du sondage",
                custom_id="sub",
                min_length=1,
                max_length=30,
            ),
        ],
    )
    await ctx.popup(modal)


@bot.modal("calendar_form")
async def modal_response(ctx, title_emb: str, start: str, duration: str, sub: str):
    nb_jours: int = int(duration) if int(duration) < 19 else 18
    list_days: list = ["Lundi", "Mardi", "Mercredi",
                       "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    my_embed = discord.Embed(
        title=title_emb,
        description="Votez pour les dates qui vous conviennent !",
        color=0xF9BEE4
    )

    increment: int = int(5) if int(5) > 0 else 0
    liste_lettres = list(ascii_uppercase)
    liste_jours: dict = dict()
    for day in range(1, nb_jours+1, 1):
        future = datetime.datetime.today() + datetime.timedelta(days=day+increment)
        horaire = f"21h, ou peut être placé en journée si préférable." if future.weekday(
        ) >= 5 else "21h tapantes, essayez d'être à l'heure !"
        liste_jours[f"{liste_lettres[day-1]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = horaire

    auteur: str = ((str(ctx.author)).split("#"))[0]
    my_embed.set_author(name=f"{auteur}", url="https://twitter.com/Tharos_le_Vif",
                        icon_url="https://media.discordapp.net/attachments/555328372213809153/946500250422632479/logo_discord.png")

    for key, value in liste_jours.items():
        my_embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    my_embed.set_footer(
        text="Après vote, merci de cliquer sur la case \U00002705 !")

    await ctx.send("Commande par Tharos, merci de répondre au plus vite !", embeds=my_embed, ephemeral=True)
"""

################ Commandes GSHEETS #################


def stat_from_player(stat, joueur):
    stats = get_stats(joueur)
    if stats != None:
        return get_stats(joueur)[stat]
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
def increase_on_crit(stat: str, name: str, valeur=1):
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
def hero_point_update(name: str, checking: bool) -> bool:
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
def get_stress(name: str):
    """
    Renvoie la valeur de stress pour le jet de dés
    * name (str) : nom du joueur
    """
    return gc.open(dict_links[f"{name}"])[0].cell('G31').value


@googleask
def get_stats(name: str) -> dict:
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

################ Pour lancer un dé #################


def roll_the_dice(message, faces, modificateur: int = 0, valeur_difficulte: int = 0, hero_point: bool = False, stat_testee: str = "") -> str:
    res = randrange(1, faces)  # jet de dé
    value = res + modificateur  # valeur globale du jet
    if stat_testee != "":
        stat_testee = f"({stat_testee})"
    if hero_point_update(message.author.mention, hero_point):
        value += modificateur
    if valeur_difficulte > 0:
        if res == faces:
            anim = "R_CRIT.avi"
            str_resultat = f"{message.author.mention} > **REUSSITE CRITIQUE** {stat_testee}\n> {res}/{faces} (dé) + {modificateur} (bonus) = **{value}** pour une difficulté de **{valeur_difficulte}**\n> *{choice(quotes['REUSSITE CRITIQUE'])}*"
        elif res == 1:
            anim = "E_CRIT.avi"
            str_resultat = f"{message.author.mention} > **ECHEC CRITIQUE** {stat_testee}\n> {res}/{faces} (dé) + {modificateur} (bonus) = **{value}** pour une difficulté de **{valeur_difficulte}**\n> *{choice(quotes['ECHEC CRITIQUE'])}*"
        elif value >= valeur_difficulte:
            anim = "R_STD.avi"
            str_resultat = f"{message.author.mention} > **REUSSITE** {stat_testee}\n> {res}/{faces} (dé) + {modificateur} (bonus) = **{value}** pour une difficulté de **{valeur_difficulte}**\n> *{choice(quotes['REUSSITE'])}*"
        else:
            anim = "E_STD.avi"
            str_resultat = f"{message.author.mention} > **ECHEC** {stat_testee}\n> {res}/{faces} (dé) + {modificateur} (bonus) = **{value}** pour une difficulté de **{valeur_difficulte}**\n> *{choice(quotes['ECHEC'])}*"
    else:
        anim = ""
        str_resultat = f"{message.author.mention} > **INCONNU** {stat_testee}\n> Le résultat du dé est **{value}** ({res}/{faces}+{modificateur}) !\n> *{choice(quotes['INCONNU'])}*"
    return (str_resultat, anim)


@bot.command(
    name="stat",
    description="Jet d'un dé accordément à votre fiche de stats !",
    scope=guild_id,
    options=[
        interactions.Option(
            name="charac",
            description="Caractéristique à tester !",
            type=interactions.OptionType.STRING,
            choices=stats_choices,
            required=True,
        ),
        interactions.Option(
            name="valeur_difficulte",
            description="Palier à atteindre pour considérer le jet réussi",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="point_heroisme",
            description="Point rendant le jet automatiquement réussi",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def stat(ctx: interactions.CommandContext, charac: str, valeur_difficulte: int = -1, point_heroisme: bool = False):
    values = stat_from_player(charac, ctx.author.mention)[2:].split('+')
    (message, anim): tuple = roll_the_dice(ctx, int(values[0]), int(values[1]), valeur_difficulte, hero_point=point_heroisme, stat_testee=charac)
    obs_invoke(toggle_anim, anim)
    await ctx.send(message)


def roll_the_stress(message, val_stress):
    """
    Lance un dé de stress et en traite les conséquences

    Keywords arguments:
    *message* (discord.message) > source de la commande
    *val_stress* (str) > valeur du stress indiqué dans le message
    """
    dice: int = randrange(1, 10)
    index: int = dice + int(val_stress)
    state, anim = listStates[index], str(
        listStates[index])[:-2]+".avi"
    effect = listEffects[index]

    if(dice >= 8):
        "Effet de stress négatif"
        quote = choice(quotes["STRESS NEGATIF"])
        increase_on_crit(
            'Stress', str(message.author.mention), 1)
    elif(dice <= 2):
        "Effet de stress positif"
        quote = choice(quotes["STRESS POSITIF"])
        increase_on_crit(
            'Stress', str(message.author.mention), -1)
    else:
        "Effet de stress médian"
        quote = choice(quotes["STRESS NEUTRE"])

    string = f"{message.author.mention} > **{state}**\n> {dice+1} (dé) : {effect}\n> *{quote}*"
    return (string, anim)


@bot.command(
    name="stress",
    description="Lance un jet de stress !",
    scope=guild_id,
)
async def stress(ctx: interactions.CommandContext):
    (message, anim): tuple = roll_the_stress(ctx, get_stress(ctx.author.mention))
    obs_invoke(toggle_anim, anim)
    await ctx.send(message)


@bot.command(
    name="dice",
    description="Simule un dé à n faces !",
    scope=guild_id,
    options=[
        interactions.Option(
            name="faces",
            description="Nombre de faces du dé à lancer",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="modificateur",
            description="Opérateur et valeur",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="valeur_difficulte",
            description="Palier à atteindre pour considérer le jet réussi",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="point_heroisme",
            description="Point rendant le jet automatiquement réussi",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def dice(ctx: interactions.CommandContext, faces: int = 20, modificateur: int = 0, valeur_difficulte: int = -1, point_heroisme: bool = False):
    (message, anim): tuple = roll_the_dice(ctx, faces, modificateur, valeur_difficulte, point_heroisme)
    obs_invoke(toggle_anim, anim)
    await ctx.send(message)


@bot.command(
    name="toss",
    description="Lance une pièce !",
    scope=guild_id,
)
async def toss(ctx: interactions.CommandContext) -> None:
    res = "**PILE**" if(random() > 0.5) else "**FACE**"
    await ctx.send(f"{ctx.author.mention} > La pièce est tombée sur {res} !\n> *Un lancer de pièce, pour remettre son sort au destin...*")


bot.start()
