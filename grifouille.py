
import interactions
from interactions.ext.files import command_send
from random import randrange, random, choice
from lib import load_json, save_json, create_char, get_personnas, get_scene_list, switch, create_stats
from pygsheets import authorize
from obs_interactions import obs_invoke, toggle_anim
from gsheets_interactions import stat_from_player, hero_point_update, increase_on_crit, get_stress
from time import sleep

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

# liste des scènes disponibles au switch
list_of_scenes: list = get_scene_list(tokens_obsws)[:20]
abbrev_scenes: list = [sc[:20] if len(
    sc) > 20 else sc for sc in list_of_scenes]

# listes utiles à déclarer en amont
list_letters: list = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9", "\U0001F1EA", "\U0001F1EB", "\U0001F1EC", "\U0001F1ED",
                      "\U0001F1EE", "\U0001F1EF", "\U0001F1F0", "\U0001F1F1", "\U0001F1F2", "\U0001F1F3", "\U0001F1F4", "\U0001F1F5", "\U0001F1F6", "\U0001F1F7"]
descs_jdr: list = ["Liens utiles aux JdR", "Retrouvez ici tous les liens pouvant vous servir durant les séances, n'oubliez pas non plus d'ouvrir votre petite fiche de personnage !",
                   "En espérant que cela vous ait été utile !"]
descs_projets: list = ["Liens vers mes projets", "Retrouvez tous les liens vers les projets ici ; tout n'est pas directement en lien avec le JdR mais parfois plus largement avec mes projets !",
                       "Merci pour tous vos partages et vos retours, c'est adorable !"]
list_days: list = ["Lundi", "Mardi", "Mercredi",
                   "Jeudi", "Vendredi", "Samedi", "Dimanche"]
manuels: list = ["one_shot"]

stats_choices: list = [interactions.Choice(
    name=val, value=val) for val in dict_stats.values()]
char_choices: list = [interactions.Choice(
    name=val, value=key) for key, val in get_personnas().items()]
# scene_choices: list = [interactions.Choice(name=abbrev, value=str(i)) for i, abbrev in enumerate(abbrev_scenes)]
scene_choices: list = [interactions.Choice(
    name=name_scene, value=name_scene) for name_scene in list_of_scenes]
manuel_choices: list = [interactions.Choice(
    name=name_manual, value=name_manual) for name_manual in manuels]

######################## Autorégie ########################


@bot.command(
    name="scene_switch",
    description="Change la scène actuelle",
    scope=guild_id,
    options=[
        interactions.Option(
            name="scene",
            description="Scène vers laquelle switch",
            type=interactions.OptionType.STRING,
            choices=scene_choices,
            required=True,
        )
    ],
)
async def scene_switch(ctx: interactions.CommandContext, scene: str):
    """_summary_

    Args:
        ctx (interactions.CommandContext): _description_
        scene (str): _description_
    """
    await ctx.defer()
    switch(tokens_obsws, scene)
    await ctx.send(f"La scène a été changée pour {scene}", ephemeral=True)


#################### Obtenir une fiche de règles ##################

@bot.command(
    name="get_manual",
    description="Renvoie un résumé de règles du système demandé",
    scope=guild_id,
    options=[
        interactions.Option(
            name="manuel",
            description="Manuel à afficher",
            type=interactions.OptionType.STRING,
            choices=manuel_choices,
            required=True,
        )
    ],
)
async def get_manual(ctx: interactions.CommandContext, manuel: str):
    await command_send(ctx, "Voici le manuel demandé !", files=interactions.File(filename=f"img/{manuel}.png"))

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
    await command_send(ctx, '\n'.join([f"*{k}*  -->  **{v}**" for k, v in create_char(type).items()]), files=interactions.File(filename=create_stats()))


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
        ],  # type: ignore
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
    message = ""
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
        await ctx.send(str(message))


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

    if (dice >= 8):
        "Effet de stress négatif"
        quote = choice(quotes["STRESS NEGATIF"])
        increase_on_crit(str(message.author.mention),
                         dict_links, gc, 'Stress', dict_pos,  1)
    elif (dice <= 2):
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
    """_summary_

    Args:
        ctx (interactions.CommandContext): _description_
    """
    message = ""
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
        await ctx.send(str(message))


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
    res = "**PILE**" if (random() > 0.5) else "**FACE**"
    await ctx.send(f"{ctx.author.mention} > La pièce est tombée sur {res} !\n> *Un lancer de pièce, pour remettre son sort au destin...*")


@bot.command(
    name="calendar",
    description="Crée un sondage de disponibilités",
    scope=guild_id,
    options=[
        interactions.Option(
            name="duree",
            description="Nombre de jours sur lequel s'étend le sondage. Maximum : 12, défaut : 7.",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="delai",
            description="Décalage de début du sondage (en jours). Défaut : 0.",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="titre",
            description="Texte de titre du sondage.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def calendar(ctx: interactions.CommandContext, duree: int = 7, delai: int = 0, titre: str = "Date pour la prochaine séance !") -> None:
    """Crée un calendrier sous forme d'embed, pour faire un sondage sur les jours suivants

    Args:
        ctx (interactions.CommandContext): contexte de la commande
        days (int, optional): Période de temps sur laquelle s'étend le sondage. Defaults to 7.
        offset (int, optional): Décalage en jours. Defaults to 0.
        description (str, optional): Un titre pour le sondage. Defaults to "Date pour la prochaine séance !".
    """
    nb_jours: int = duree if duree <= 12 and duree > 0 else 7
    decalage: int = delai if delai >= 0 else 0
    list_days: list = ["Lundi", "Mardi", "Mercredi",
                       "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    list_letters: list = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9", "\U0001F1EA", "\U0001F1EB", "\U0001F1EC", "\U0001F1ED",
                          "\U0001F1EE", "\U0001F1EF", "\U0001F1F0", "\U0001F1F1", "\U0001F1F2", "\U0001F1F3", "\U0001F1F4", "\U0001F1F5", "\U0001F1F6", "\U0001F1F7"]
    liste_lettres = list(ascii_uppercase)
    liste_jours: dict = dict()
    step: int = 0

    # on itère à travers les jours
    for day in range(1, nb_jours+1, 1):
        future = datetime.today() + timedelta(days=day+decalage)
        horaire: str | list = ["Rassemblement 9h45, début 10h !", "Rassemblement 13h45, début 14h !", "Rassemblement 20h45, début 21h !"] if future.weekday(
        ) >= 5 else "Rassemblement 20h45, début 21h !"
        if isinstance(horaire, list):
            for h in horaire:
                liste_jours[f"{liste_lettres[step]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = h
                step += 1
        else:
            liste_jours[f"{liste_lettres[step]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = horaire
            step += 1

    # on définit une lise d'emoji de la longueur du nombre de réponses possibles
    list_emoji: list = [list_letters[i]
                        for i in range(step)] + ["\U00002705"] + ["\U0000274C"]

    # role = await interactions.get(bot, interactions.Role, object_id=ROLE_ID, parent_id=GUILD_ID) ajouter à embed.description les rôles à tag , avec champ de liste ?
    embed = interactions.Embed(title=titre)

    for key, value in liste_jours.items():
        embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    emoji = interactions.Emoji(
        name="patounes_tongue",
        id=979488514561421332
    )

    msg = await ctx.message.channel.send(f"Merci de répondre au plus vite {emoji}", embeds=embed)
    # affiche les réactions pour le sondage
    for emoji in list_emoji:
        await msg.add_reaction(emoji)


if __name__ == "__main__":
    bot.load('interactions.ext.files')
    while (True):
        try:
            bot.start()
        except KeyboardInterrupt:
            print(KeyboardInterrupt("Keyboard interrupt, terminating Grifouille"))
            exit()
        except:
            sleep(10)
