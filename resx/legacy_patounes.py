# A REBUILD
import resx.pnj as p
import resx.loader as l
import datetime
# OK
from discord import Embed, Client, Streaming, File, FFmpegPCMAudio
from os import fsencode, fsdecode, listdir
from random import random, choice, randrange
from sys import path
from pygsheets import authorize
from string import ascii_uppercase
from lib import output_msg, load_json, save_json, Wrapped_Exception, Sheets_Exception, YTDLSource
from obs_interactions import obs_invoke, toggle_anim
from gsheets_interactions import stat_from_player, increase_on_crit, get_stress

##################### TOKENS DE CONNEXION ##########################


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


# tokens OBS-WS
tokens_obsws: dict = load_json("obs_ws")
host: str = tokens_obsws["host"]
port: int = tokens_obsws["port"]
password: str = tokens_obsws["password"]

# tokens GSheets
gc = authorize(service_file='env/connect_sheets.json')

# tokens discord
tokens_connexion: dict = load_json("connect_discord")
token: str = tokens_connexion['cle_de_connexion']
admin: str = tokens_connexion['administrator']

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

# chaines utiles
help_string: str = "Vous pouvez utiliser les commandes :\n" + \
    "\n".join([f"**{key}** - *{val}*" for key,
              val in load_json("helps").items()])

############################### WRAPPER #################################


def commande(func):
    def wrapper(*args, **kwargs):
        """
        Effectue l'affichage du message retour
        Format des fonctions @commande : doivent retourner un dico d'éléments
        """
        dict_retour = func(*args, **kwargs)
        if dict_retour == None:
            raise Wrapped_Exception("Aucun retour par la fonction.")
        message = args[0]

        # préparation des retours
        infos_retour = f"Commande par {message.author.mention} > {dict_retour['info']}\n" if 'info' in dict_retour else ""
        chaine_retour = dict_retour['chaine']

        if(isinstance(dict_retour['chaine'], str)):
            # affiche dans la console ssi c'est une chaine
            output_msg(chaine_retour.replace('\n', ' '))
        return (chaine_retour, infos_retour)
    return wrapper


@commande
def gennom(message, ld) -> dict:
    "Génère un nom aléatoire"
    return {'info': 'Voici le nom demandé !', 'chaine': p.Pnj(ld).name}


@commande
def savefile(message) -> dict:
    """
    Associe une fiche de stats à un ID discord
    et enregistre la fiche de liens discord-gsheets
    """
    file_name = (message.content).split(' ')[1]
    dict_links[f"{message.author.mention}"] = f"{file_name}"
    save_json("links", dict_links)
    return {'info': 'La fiche a bien été associée !', 'chaine': f"Le nom de la fiche est {file_name}"}


@commande
def genpnj(message, ld) -> dict:
    "Génère un PnJ complet"
    monPnj, string = p.Pnj(ld), ""
    for key in monPnj.carac:
        string = string + f"**{key.replace('_',' ')}** = {monPnj.carac[key]}\n"
    return {'info': 'Voici le PnJ demandé !', 'chaine': string}


@commande
def toss(message) -> dict:
    string = "**PILE**" if(random() > 0.5) else "**FACE**"
    return {'info': string, 'chaine': '> *Un lancer de pièce, pour remettre son sort au destin...*'}


@commande
def meow(message) -> dict:
    list_meows = [
        "img/happy_cat.gif",
        "img/manul_cat.gif",
        "img/water_cat.gif",
        "img/love_cat.gif",
        "img/eyes_cat.gif"
    ]
    return {'info': 'Meow', 'chaine': choice(list_meows)}


@commande
def disconnect(message, client) -> dict:
    """
    TODO fix la fonction
    Déconnecte le client de manière safe
    """
    if(str(message.author.id) == str(admin)):
        client.close()
        return {'info': 'Tentative de déconnexion...', 'chaine': "Déconnexion du serveur. A bientôt !"}
    else:
        return {'info': 'Tentative de déconnexion...', 'chaine': "Vous n'avez pas les droits pour déconnecter le bot."}


@commande
def weekpoll(message, client, chaine: str | None = None, jours: int = 9, incr: int = 0) -> dict:
    """
    Renvoie un embed discord de sondage

    message:discord.message = le message envoyé par l'utilisateur
    client:discord.client = le client responsable de l'IO du bot
    nb_jours:int (9) = le nombre de jours sur lequel le sondage s'exécute, max. 19
    incr:int (0) = le nombre de jours dans lequel la première date du sondage est posée
    """
    nb_jours: int = int(jours) if int(jours) < 20 else 19
    list_days: list = ["Lundi", "Mardi", "Mercredi",
                       "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    # pour pouvoir générer un futur plus ou moins lointain, s'exprime en nombre de jours
    increment: int = int(incr) if int(incr) > 0 else 0
    liste_lettres = list(ascii_uppercase)
    liste_jours: dict = dict()
    for day in range(1, nb_jours+1, 1):
        future = datetime.datetime.today() + datetime.timedelta(days=day+increment)
        horaire = f"21h, ou peut être placé en journée si préférable." if future.weekday(
        ) >= 5 else "21h tapantes, essayez d'être à l'heure !"
        liste_jours[f"{liste_lettres[day-1]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = horaire
    title_poll = chaine if chaine != None else "Date pour la prochaine séance !"
    embed = Embed(title=title_poll,
                  description="Votez pour les dates qui vous conviennent :)", color=0xF9BEE4)
    auteur: str = ((str(message.author)).split("#"))[0]
    embed.set_author(name=f"{auteur}", url="https://twitter.com/Tharos_le_Vif",
                     icon_url="https://media.discordapp.net/attachments/555328372213809153/946500250422632479/logo_discord.png")

    for key, value in liste_jours.items():
        embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    embed.set_footer(
        text="Après vote, merci de cliquer sur la case \U00002705 !")
    meow_emoji = client.get_emoji(906137086262923275)

    return {'info': f"Merci de répondre au plus vite {meow_emoji}", 'chaine': embed}


@commande
def embedlink(message, dico: dict, descs: str):
    embed = Embed(title=descs[0], description=descs[1], color=0xF9BEE4)
    embed.set_author(name="Tharos", url="https://twitter.com/Tharos_le_Vif",
                     icon_url="https://media.discordapp.net/attachments/555328372213809153/946500250422632479/logo_discord.png")
    for key, value in dico.items():
        embed.add_field(
            name=key, value=f"[{value[0]}]({value[1]})", inline=False)

    embed.set_footer(text=descs[2])

    return {'info': "Voici les liens demandés", 'chaine': embed}

####################################################################


def roll_the_stress(message, val_stress):
    """
    Lance un dé de stress et en traite les conséquences

    Keywords arguments:
    *message* (discord.message) > source de la commande
    *val_stress* (str) > valeur du stress indiqué dans le message
    """
    dice: int = randrange(0, 10) + 1
    index: int = dice + int(val_stress)
    state, anim = listStates[index], str(
        listStates[index])[:-2]+".avi"
    effect = listEffects[index]

    if(dice >= 8):
        "Effet de stress négatif"
        quote = quote_selection("STRESS NEGATIF")
        increase_on_crit(str(message.author.mention),
                         dict_links, gc, 'Stress', dict_pos, 1)
    elif(dice <= 2):
        "Effet de stress positif"
        quote = quote_selection("STRESS POSITIF")
        increase_on_crit(str(message.author.mention),
                         dict_links, gc, 'Stress', dict_pos, -1)
    else:
        "Effet de stress médian"
        quote = quote_selection("STRESS NEUTRE")

    string = f"{message.author.mention} > **{state}**\n> {dice+1} (dé) : {effect}\n> *{quote}*"
    output_msg(string)
    return (string, anim)


def roll_the_dice(de_a_lancer: int, bonus: int, message, valeur_difficulte: int = 0, statistique: str = ""):
    """Permet de lancer un dé, et retourne une chaine formatée indiquant le résultat du jet.
    Effet de bord : envoie une animation sur OBS Studio

    Keywords arguments:
    *de_a_lancer* (int) > valeur de lancer du dé
    *bonus* (int) > bonus à ajouter au dé
    *valeur_difficulte* (int) > valeur à laquelle comparer, si elle existe (par def : 0)
    *message* (discord.message) > objet message discord
    """
    dice: int = randrange(0, int(de_a_lancer))+1
    resultat: int = int(dice) + int(bonus)
    if dice == 1:
        state, anim = "ECHEC CRITIQUE", "E_CRIT.avi"
    elif dice == de_a_lancer:
        state, anim = "REUSSITE CRITIQUE", "R_CRIT.avi"
        if(statistique != ""):
            increase_on_crit(str(message.author.mention),
                             dict_links, gc, 'Stress', dict_pos, 1)
    else:
        if valeur_difficulte == 0:
            state, anim = "INCONNU", ""
        else:
            if resultat >= valeur_difficulte:
                state, anim = "REUSSITE", "R_STD.avi"
            else:
                state, anim = "ECHEC", "E_STD.avi"
    string = f"{message.author.mention} > **{state}** {statistique}\n> {dice}/{de_a_lancer} (dé) + {bonus} (bonus) = {resultat} pour une difficulté de {valeur_difficulte}\n> *{quote_selection(state)}*" if valeur_difficulte != 0 else f"{message.author.mention} > **{state}** {statistique}\n> {dice}/{de_a_lancer} (dé) + {bonus} (bonus) = {resultat}\n> *{quote_selection(state)}*"
    output_msg(string)
    return (string, anim)


async def error_nofile(client, message) -> None:
    meow_emoji = client.get_emoji(906136078472331284)
    await message.channel.send(f"Désolé {message.author.mention} > tu n'as pas de fiche nommée sur GoogleSheets {meow_emoji}")
    raise Sheets_Exception("Pas de feuille valide")


async def delete_command(message) -> None:
    "Supprime le message à l'origine de la commande"
    messages = await message.channel.history(limit=1).flatten()
    for each_message in messages:
        await each_message.delete()


def string_cleaner(chaine: str) -> str:
    """
    Nettoie une chaine d'entrée
    """
    return chaine.replace(' ', '')


def quote_selection(categorie: str) -> str:
    "Renvoie une quote issue du dico de quotes qui match la catégorie"
    return choice(quotes[categorie])


async def sender(chaine, message):
    "Envoie le message {chaine} dans le chan de la commande"
    await message.channel.send(chaine)


async def send_texte(chaine, message):
    "Envoie le message {chaine} dans le chan de la commande"
    await message.channel.send(chaine)


async def send_embed(txt, emb, message):
    "Envoie le message d'embed"
    await message.channel.send(txt, embed=emb)


async def send_image(txt, img, message):
    "Envoie une potite image"
    await message.channel.send(txt, file=File(img))


def bot(ld):
    client = Client()

    @client.event
    async def on_ready():
        await client.change_presence(activity=Streaming(name="!support", url="https://www.twitch.tv/TharosTV"))
        output_msg(f"PATOUNES EST PRET !")

    @client.event
    async def on_message(message):
        contents: str = message.content

        # nettoyage
        if(contents in ["!join", "!leave", "!pause", "!resume", "!stop", "!savelink", "!toss", "!disconnect", "!support", "!gennom", "!genpnj", "!meow", "!linkjdr", "!linkprojet"] or contents[:5] in ["!play"] or contents[:2] in ["!d", "!s", "!r"] or contents[:3] in ["!wp"] or contents[:4] in dict_stats.keys()):
            output_msg(
                f"Réception d'une commande de {str(message.author)} > {contents}")
            await delete_command(message)

            match contents:

                case "!join":

                    if not message.author.voice:
                        await send_texte("Désolé, tu n'es pas dans un chan vocal :(", message)
                        return
                    else:
                        channel = message.author.voice.channel
                    await channel.connect()

                case "!leave":

                    voice_client = message.guild.voice_client
                    if voice_client.is_connected():
                        await voice_client.disconnect()
                    else:
                        await send_texte("Désolé, le bot est déjà déconnecté :(", message)

                case "!linkprojet":
                    "Donne les liens vers les différents projets sous forme d'un embed"
                    eb = embedlink(message, embed_projets, descs_projets)
                    await send_embed(eb[1], eb[0], message)

                case "!linkjdr":
                    "Donne les liens vers les différents outils pour les JdR sous forme d'un embed"
                    eb = embedlink(message, embed_jdr, descs_jdr)
                    await send_embed(eb[1], eb[0], message)

                case '!support':
                    "Renvoie l'aide du bot"
                    await send_texte(help_string, message)

                case "!gennom":
                    "Renvoie une génération de nom à l'utilisateur"
                    tmp = gennom(message, ld)
                    await send_texte(f"{tmp[1]}{tmp[0]}", message)

                case "!genpnj":
                    "Renvoie une génération de pnj à l'utilisateur"
                    tmp = genpnj(message, ld)
                    await send_texte(f"{tmp[1]}{tmp[0]}", message)

                case "!meow":
                    "Envoi d'un gif de chat"
                    tmp = meow(message)
                    await send_image(tmp[1], tmp[0], message)

                case "!disconnect":
                    "Tentative de déconnexion, utilisable seulement par un admin"
                    await send_texte(disconnect(message), message)

                case "!toss":
                    "Lance une pièce et donne un résultat pile/face"
                    tmp = toss(message)
                    await send_texte(f"{tmp[1]}{tmp[0]}", message)

                case _:

                    if contents[:5] == "!play":

                        url: str = contents.split()[1]
                        server = message.guild
                        voice_channel = server.voice_client

                        filename = await YTDLSource.from_url(url, loop=client.loop)
                        try:
                            voice_channel.play(FFmpegPCMAudio(
                                executable="ffmpeg", source=filename))
                            await send_texte(f'**Joue :** {filename}', message)
                        except:
                            await send_texte("Désolé, le bot n'est pas connecté :(", message)

                    elif contents[:9] == "!savefile":
                        "Crée un lien symbolique entre un ID discord et une fiche"
                        tmp = savefile(message)
                        await send_texte(f"{tmp[1]}{tmp[0]}", message)

                    # dé fonctionnant avec le nom du joueur, va chercher la stat
                    elif(contents[:4] in dict_stats.keys()):
                        contents = string_cleaner(contents)

                        stat = stat_from_player((str(message.author.mention)).split(
                            "#")[0], dict_links, gc, dict_stats[contents[:4]])[2:]
                        if stat != None:
                            valeur_difficulte = contents.split(
                                "/")[1] if "/" in contents else 0
                            de_a_lancer = stat.split(
                                "+")[0] if '+' in stat else stat
                            bonus = stat.split(
                                "+")[1] if '+' in stat else 0

                            output = roll_the_dice(int(de_a_lancer), int(bonus), message, int(
                                valeur_difficulte), f"({dict_stats[contents[:4]]})")

                            await sender(output[0], message)
                            # system(f"python obs.py {output[1]}")
                            await obs_invoke(toggle_anim, host, port, password, output[1])

                        # erreur si on la trouve pas
                        else:
                            await error_nofile(client, message)

                    # dé simple avec ou sans valeur de difficulté
                    elif(contents[:2] == '!d'):
                        # contents = string_cleaner(contents)
                        datas = contents[2:]

                        de_a_lancer = (datas.split("+")[0]).split("/")[0]
                        reste = datas.split("+")[1] if '+' in datas else None

                        if reste == None:
                            reste = datas.split(
                                "/")[1] if "/" in datas else None

                        diff, bonus = 0, 0

                        if reste != None:
                            diff = datas.split('/')[1] if '/' in datas else 0
                            bonus = reste.split(
                                '/')[0] if '+' in datas else 0

                        output = roll_the_dice(
                            int(de_a_lancer), int(bonus), message, int(diff))

                        await sender(output[0], message)
                        await obs_invoke(toggle_anim, host, port, password, output[1])

                    elif(contents[:2] == '!s'):  # lancer de dé de stress
                        if (contents[2:] != ''):
                            val_stress: int = int(contents[2:])
                        else:
                            val_stress: int = get_stress(
                                str(message.author.mention), dict_links, gc)
                            if(val_stress != None):

                                string, anim = roll_the_stress(
                                    message, val_stress)

                                await sender(string, message)
                                await obs_invoke(toggle_anim, host, port, password, anim)

                            else:
                                await error_nofile(client, message)

                    elif(contents[:3] == '!wp'):
                        "Renvoie un sondage paramétré"
                        valeurs: str = string_cleaner(
                            contents[3:].split('|')[0])
                        nb_jours: int = int(valeurs.split(
                            '+')[0]) if '+' in valeurs else 9
                        decalage: int = int(valeurs.split(
                            '+')[1]) if '+' in valeurs else 0
                        chaine = contents[3:].split(
                            '|')[1] if '|' in contents[3:] else None
                        sondage = weekpoll(
                            message, client, chaine, nb_jours, decalage)
                        msg = await message.channel.send(sondage[1], embed=sondage[0])

                        # affiche les réactions pour le sondage

                        list_emoji = [list_letters[i]
                                      for i in range(0, nb_jours, 1)] + ["\U00002705"] + ["\U0000274C"]
                        for emoji in list_emoji:
                            await msg.add_reaction(emoji)

    client.run(token)


def main():
    liste_dicos = dict()
    directory_in_str = "resx/"
    directory = fsencode(directory_in_str)
    for file in listdir(directory):
        filename = fsdecode(file)
        if filename.endswith(".ini"):
            liste_dicos[filename] = l.Loader(f"{directory_in_str}{filename}")
    # dico par défaut
    ld = liste_dicos[list(liste_dicos.keys())[0]] if liste_dicos != dict(
    ) else l.Loader("data/data.ini")
    bot(ld)


if __name__ == "__main__":
    path.append('../')
    main()
