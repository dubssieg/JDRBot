from re import S
import interactions
from random import randrange, random, choice
from lib import load_json, save_json, create_char, get_personnas
from pygsheets import authorize
from obs_interactions import obs_invoke, toggle_anim
from gsheets_interactions import stat_from_player, hero_point_update, increase_on_crit, get_stress

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

# déclaration du client
bot = interactions.Client(
    token=token_grifouille)

# tokens GSheets
gc = authorize(service_file='env/connect_sheets.json')

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
char_choices: list = [interactions.Choice(
    name=val, value=key) for key, val in get_personnas().items()]

#################### Créer un personnage ##################


@bot.command(
    name="create_char",
    description="Génère les caractéristiques d'un personnage aléatoire !",
    scope=guild_id,
    options=[
        interactions.Option(
            name="type",
            description="Type de personnage à générer",
            type=interactions.OptionType.STRING,
            choices=char_choices,
            required=True,
        )
    ],
)
async def generate_char(ctx: interactions.CommandContext, type: str):
    await ctx.send('\n'.join([f"*{k}*  -->  **{v}**" for k, v in create_char(type).items()]), ephemeral=True)

    ################ Pour demander la fiche #################


@bot.command(
    name="save_file",
    description="Sauvegarde un lien avec une fiche de statisitiques",
    scope=guild_id,
)
async def save_file(ctx):
    modal2 = interactions.Modal(
        title="Lier une feuille de stats",
        custom_id="mod_app_form",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Entrez le nom de votre fiche sur GoogleSheets",
                custom_id="text_input_response",
                min_length=1,
                max_length=50,
            )
        ],
    )
    await ctx.popup(modal2)


@bot.modal("mod_app_form")
async def modal_response(ctx, response: str):
    await ctx.defer()
    dict_links[f"{ctx.author.mention}"] = f"{response}"
    save_json('links', dict_links)
    await ctx.send(f"La fiche nommée {response} vous a été liée !", ephemeral=True)


################ Pour lancer un dé #################


def roll_the_dice(message, faces, modificateur: int = 0, valeur_difficulte: int = 0, hero_point: bool = False, stat_testee: str = "") -> str:
    res = randrange(1, faces)  # jet de dé
    value = res + modificateur  # valeur globale du jet
    if stat_testee != "":
        stat_testee = f"({stat_testee})"
    if hero_point_update(message.author.mention, dict_links, gc, hero_point):
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
    """Lance un dé d'une statistique associée à une fiche google sheets

    Args:
        ctx (interactions.CommandContext): contexte d'envoi du message
        charac (str): la caractéristique à tester
        valeur_difficulte (int, optional): difficulté à battre ou égaler pour que le jet soit une réussite. Defaults to -1.
        point_heroisme (bool, optional): stipule si on tente d'utiliser son point d'héroïsme. Defaults to False.
    """
    await ctx.defer()
    try:
        values = stat_from_player(ctx.author.mention, dict_links, gc, charac)[
            2:].split('+')
        message, anim = roll_the_dice(ctx, int(values[0]), int(
            values[1]), valeur_difficulte, hero_point=point_heroisme, stat_testee=charac)
        await obs_invoke(toggle_anim, host, port, password, anim)
    except ConnectionError:
        message = ConnectionError(
            f"Impossible d'atteindre la valeur de {charac} pour {ctx.author.mention}.")
    except ValueError:
        message = ValueError(
            f"Désolé {ctx.author.mention}, tu ne sembles pas avoir de fiche liée dans ma base de données.")
    finally:
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
        increase_on_crit(str(message.author.mention),
                         dict_links, gc, 'Stress', dict_pos,  1)
    elif(dice <= 2):
        "Effet de stress positif"
        quote = choice(quotes["STRESS POSITIF"])
        increase_on_crit(str(message.author.mention),
                         dict_links, gc, 'Stress', dict_pos,  -1)
    else:
        "Effet de stress médian"
        quote = choice(quotes["STRESS NEUTRE"])

    string = f"{message.author.mention} > **{state}**\n> {dice+1} (dé) : {effect}\n> *{quote}*"
    return (string, anim)


@ bot.command(
    name="stress",
    description="Lance un jet de stress !",
    scope=guild_id,
)
async def stress(ctx: interactions.CommandContext):
    await ctx.defer()
    try:
        message, anim = roll_the_stress(
            ctx, get_stress(ctx.author.mention, dict_links, gc))
        await ctx.send(message)
        await obs_invoke(toggle_anim, host, port, password, anim)
    except ConnectionError:
        message = ConnectionError(
            f"Impossible d'atteindre la valeur de stress pour {ctx.author.mention}.")
    except ValueError:
        message = ValueError(
            f"Désolé {ctx.author.mention}, tu ne sembles pas avoir de fiche liée dans ma base de données.")
    finally:
        await ctx.send(message)


@ bot.command(
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
    await ctx.defer()
    message, anim = roll_the_dice(
        ctx, faces, modificateur, valeur_difficulte, point_heroisme)
    await ctx.send(message)
    await obs_invoke(toggle_anim, host, port, password, anim)


@bot.command(
    name="toss",
    description="Lance une pièce !",
    scope=guild_id,
)
async def toss(ctx: interactions.CommandContext) -> None:
    await ctx.defer()
    res = "**PILE**" if(random() > 0.5) else "**FACE**"
    await ctx.send(f"{ctx.author.mention} > La pièce est tombée sur {res} !\n> *Un lancer de pièce, pour remettre son sort au destin...*")

bot.start()
