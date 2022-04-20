
from obswebsocket import obsws, requests
import discord
import pygsheets
import resx.pnj as p
import resx.loader as l
import os
import random
import csv
import datetime
import sys
import logging
import asyncio
import datetime

###
from string import ascii_uppercase
from lib import output_msg, load_json, save_json, OBS_Shutdown, Max_Poll_Size, Wrapped_Exception, Sheets_Exception

##################### TOKENS DE CONNEXION ##########################

# tokens GSheets
gc = pygsheets.authorize(service_file='connectsheets-341012-fddaa9df86d9.json')

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

listStates = [key for key in dict_stress.keys()],
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

##################### GSHEETS ##########################


def stat_from_player(stat, joueur):
    stats = get_stats(joueur)
    if stats != None:
        return get_stats(joueur)[stat]
    return None


def googleask(func):
    "Décorateur. Gère si l'utilisateur a bien une fiche à son nom"
    def wrapper(*args, **kwargs):
        try:
            retour = func(*args, **kwargs)
        except:
            return None
        return retour
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
    sh = gc.open(f"OmbreMeteore_{name}")
    wks = sh[0]
    # récupération des cellules d'intérêt
    cell_list = wks.range('C12:E29')
    d = dict()
    for e in cell_list:
        d[e[0].value] = e[1].value + e[2].value
    return d


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
    "Associe une fiche de stats à un ID discord"
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
    string = "**PILE**" if(random.random() > 0.5) else "**FACE**"
    return {'info': string, 'chaine': '> *Un lancer de pièce, pour remettre son sort au destin...*'}


@commande
def meow(message) -> dict:
    list_meows = [
        "happy_cat.gif"
    ]
    return {'info': 'Meow', 'chaine': random.choice(list_meows)}


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
def weekpoll(message, client, nb_jours: int = 9, incr: int = 0) -> dict:
    """
    Renvoie un embed discord de sondage pour définir une date
    * message (discord.message) : le message envoyé par l'utilisateur
    * client (discord.client) : le client responsable de l'IO du bot
    * nb_jours (int, def 9) : le nombre de jours sur lequel le sondage s'exécute, max. 19
    * incr (int, def 0) : le nombre de jours dans lequel la première date du sondage est posée
    """
    if nb_jours > 19:
        nb_jours = 19
    # pour pouvoir générer un futur plus ou moins lointain, s'exprime en nombre de jours
    increment: int = incr if incr > 0 else 0
    liste_lettres = list(ascii_uppercase)
    liste_jours: dict = dict()
    for day in range(1, nb_jours+1, 1):
        future = datetime.datetime.today() + datetime.timedelta(days=day+increment)
        horaire = f"21h, ou peut être placé en journée si préférable." if future.weekday(
        ) >= 5 else "21h tapantes, essayez d'être à l'heure !"
        liste_jours[f"{liste_lettres[day-1]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = horaire

    embed = discord.Embed(title="Date pour la prochaine séance !",
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
    embed = discord.Embed(title=descs[0], description=descs[1], color=0xF9BEE4)
    embed.set_author(name="Tharos", url="https://twitter.com/Tharos_le_Vif",
                     icon_url="https://media.discordapp.net/attachments/555328372213809153/946500250422632479/logo_discord.png")
    for key, value in dico.items():
        embed.add_field(
            name=key, value=f"[{value[0]}]({value[1]})", inline=False)

    embed.set_footer(text=descs[2])

    return {'info': "Voici les liens demandés", 'chaine': embed}

####################################################################


async def obs_invoke(f, *args) -> None:
    "appel avec unpacking via l'étoile"
    logging.basicConfig(level=logging.INFO)

    sys.path.append('../')

    host = "localhost"
    port = 4444
    password = ""

    ws = obsws(host, port, password)
    try:
        ws.connect()
        await f(ws, args)  # exécution de la fonction
        ws.disconnect()
    except Exception:
        raise OBS_Shutdown("Impossible de se connecter à OBS Studio.")


async def toggle_anim(ws, name) -> None:
    try:
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=True))
        output_msg(f"L'animation {name} est lancée !")
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(
            scene_name="Animations", item=name[0], visible=False))

    except KeyboardInterrupt:
        pass


def roll_the_dice(de_a_lancer: int, bonus: int, message, valeur_difficulte: int = 0, statistique: str = ""):
    """Permet de lancer un dé, et retourne une chaine formatée indiquant le résultat du jet.
    Effet de bord : envoie une animation sur OBS Studio

    Keywords arguments:
    *de_a_lancer* (int) > valeur de lancer du dé
    *bonus* (int) > bonus à ajouter au dé
    *valeur_difficulte* (int) > valeur à laquelle comparer, si elle existe (par def : 0)
    *message* (discord.message) > objet message discord
    """
    dice: int = random.randrange(0, (de_a_lancer))+1
    resultat: int = dice + bonus
    if dice == 1:
        state, anim = "ECHEC CRITIQUE", "E_CRIT.avi"
    elif dice == de_a_lancer:
        state, anim = "REUSSITE CRITIQUE", "R_CRIT.avi"
        if(statistique != ""):
            increase_on_crit(statistique[1:-1], str(message.author.mention))
            # increase_on_crit(statistique, str(message.author)) <--- ????
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


def quote_selection(categorie: str) -> str:
    "Renvoie une quote issue du dico de quotes qui match la catégorie"
    return random.choice(quotes[categorie])


def sender(chaine, message):
    "Envoie le message {chaine} dans le chan de la commande"
    message.channel.send(chaine)


async def send_texte(chaine, message):
    "Envoie le message {chaine} dans le chan de la commande"
    await message.channel.send(chaine)


async def send_embed(txt, emb, message):
    "Envoie le message d'embed"
    await message.channel.send(txt, embed=emb)


async def send_image(txt, img, message):
    "Envoie une potite image"
    await message.channel.send(txt, file=discord.File(img))


def bot(ld):
    client = discord.Client()

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Streaming(name="!support", url="https://www.twitch.tv/TharosTV"))
        output_msg(f"PATOUNES EST PRET !")

    @client.event
    async def on_message(message):
        contents: str = message.content

        # nettoyage
        if(contents in ["!toss", "!disconnect", "!support", "!gennom", "!genpnj", "!meow", "!linkjdr", "!linkprojet"] or contents[:2] in ["!d", "!s", "!r"] or contents[:3] in ["!wp"] or contents[:4] in dict_stats.keys()):
            output_msg(
                f"Réception d'une commande de {str(message.author)} > {contents}")
            delete_command(message)

            match contents:

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

                case "!savefile":
                    "Crée un lien symbolique entre un ID discord et une fiche"
                    tmp = savefile(message)
                    await send_texte(f"{tmp[1]}{tmp[0]}", message)

                case _:

                    # dé fonctionnant avec le nom du joueur
                    if(contents[:4] in dict_stats.keys()):

                        stat = stat_from_player(
                            dict_stats[contents[:4]], (str(message.author)).split("#")[0])[2:]
                        if stat != None:
                            valeur_difficulte = contents.split(
                                "/")[1] if "/" in contents else 0
                            de_a_lancer, bonus = stat.split(
                                "+")[0], stat.split("+")[1]

                            output = roll_the_dice(int(de_a_lancer), int(bonus), message, int(
                                valeur_difficulte), f"({dict_stats[contents[:4]]})")

                            asyncio.gather(
                                sender(output[0], message),
                                obs_invoke(toggle_anim, output[1])
                            )
                        else:
                            await error_nofile(client, message)

                    elif(contents[:2] == '!d'):  # dé simple avec ou sans valeur de difficulté

                        datas = contents[2:].replace(
                            " ", "")  # on nettoie la chaine
                        de_a_lancer, reste = datas.split(
                            "+")[0], datas.split("+")[1]

                        diff = reste.split('/')[1] if '/' in reste else 0
                        bonus = reste.split('/')[0] if '/' in reste else reste

                        output = roll_the_dice(
                            int(de_a_lancer), int(bonus), message, int(diff))

                        asyncio.gather(
                            sender(output[0], message),
                            obs_invoke(toggle_anim, output[1])
                        )

                    elif(contents[:2] == '!s'):  # lancer de dé de stress
                        if (contents[2:] != ''):
                            val_stress: int = int(contents[2:])
                        else:
                            val_stress: int = get_stress(
                                str(message.author.mention))
                            if(val_stress != None):

                                dice: int = random.randrange(0, 10) + 1
                                index: int = dice + int(val_stress)

                                state, anim = listStates[index], str(
                                    listStates[index])[:-2]+".avi"
                                effect = listEffects[index]

                                if(dice >= 8):
                                    "Effet de stress négatif"
                                    quote = quote_selection("STRESS NEGATIF")
                                    increase_on_crit(
                                        'Stress', str(message.author.mention), 1)
                                elif(dice <= 2):
                                    "Effet de stress positif"
                                    quote = quote_selection("STRESS POSITIF")
                                    increase_on_crit(
                                        'Stress', str(message.author.mention), -1)
                                else:
                                    "Effet de stress médian"
                                    quote = quote_selection("STRESS NEUTRE")

                                string = f"{message.author.mention} > **{state}**\n> {dice+1} (dé) : {effect}\n> *{quote}*"
                                output_msg(string)

                                asyncio.gather(
                                    sender(string, message),
                                    obs_invoke(toggle_anim, anim)
                                )

                            else:
                                await error_nofile(client, message)

                    elif(contents[:3] == '!wp'):
                        "Renvoie un sondage paramétré"
                        valeurs: str = contents[3:]
                        nb_jours: int = int(valeurs.split(
                            '+')[0]) if '+' in valeurs else 9
                        decalage: int = int(valeurs.split(
                            '+')[1]) if '+' in valeurs else 0

                        sondage = weekpoll(message, client, nb_jours, decalage)
                        msg = await message.channel.send(sondage[1], embed=sondage[0])

                        # affiche les réactions pour le sondage

                        list_emoji = [list_letters[i]
                                      for i in range(0, nb_jours, 1)] + ["\U00002705"]
                        for emoji in list_emoji:
                            await msg.add_reaction(emoji)

    client.run(token)


def main():
    liste_dicos = dict()
    directory_in_str = "resx/"
    directory = os.fsencode(directory_in_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".ini"):
            liste_dicos[filename] = l.Loader(f"{directory_in_str}{filename}")
    # dico par défaut
    ld = liste_dicos[list(liste_dicos.keys())[0]] if liste_dicos != dict(
    ) else l.Loader("data/data.ini")
    bot(ld)


if __name__ == "__main__":
    main()
