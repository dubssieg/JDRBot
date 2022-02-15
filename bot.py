# from asyncio.windows_events import NULL
from multiprocessing.sharedctypes import Value
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
import json

##################### TOKENS DE CONNEXION ##########################

gc = pygsheets.authorize(service_file='connectsheets-341012-fddaa9df86d9.json')

with open("connectdiscord.json", "r") as read_file:
    tokens_connexion = json.load(read_file)

token:str = tokens_connexion['cle_de_connexion']
admin:str = tokens_connexion['administrator']

##################### CUSTOM ERRORS & STACK ##########################

class OBS_Shutdown(Exception):
    """Custom error for OBS not working"""
    def __init__(self, msg:str) -> None:
        self.__message = msg
        super().__init__(self.__message)

def output_msg(string:str) -> None:
    """Prints the date and time of action + info specified in str"""
    print(f"[{str(datetime.datetime.now())}] {string}")


##################### GSHEETS ##########################



dict_stats:dict = {
                '!par':'Parade',
                '!res':'Résistance',
                '!cou':'Course',
                '!abs':'Abstraction',
                '!mag':'Magie',
                '!con':'Connaissance',
                '!pou':'Pousser',
                '!sur':'Survie',
                '!fra':'Frappe',
                '!dec':'Déchiffrement',
                '!obs':'Observation',
                '!ref':'Réflexion',
                '!esq':'Esquive',
                '!fur':'Furtivité',
                '!pre':'Précision',
                '!art':'Arts et culture',
                '!emp':'Empathie',
                '!cha':'Charme et influence'
            }

dict_pos:dict = {
                'Parade':'E12',
                'Résistance':'E13',
                'Course':'E14',
                'Abstraction':'E15',
                'Magie':'E16',
                'Connaissance':'E17',
                'Pousser':'E18',
                'Survie':'E19',
                'Frappe':'E20',
                'Déchiffrement':'E21',
                'Observation':'E22',
                'Réflexion':'E23',
                'Esquive':'E24',
                'Furtivité':'E25',
                'Précision':'E26',
                'Arts et culture':'E27',
                'Empathie':'E28',
                'Charme et influence':'E29',
                'Stress':'G31'
            }

def stat_from_player(stat,joueur):
    return get_stats(joueur)[stat]

def increase_on_crit(stat,name,valeur=1):
    # connexion
    cellule = dict_pos[stat]
    sh = gc.open(f"OmbreMeteore_{name}")
    wks = sh[0]
    value = int(wks.cell(cellule).value)
    wks.update_value(cellule, value+valeur)

def get_stress(name):
    """Renvoie la valeur de stress pour le jet de dés
    *name* <str> : nom du joueur
    """
    return gc.open(f"OmbreMeteore_{name}")[0].cell('G31').value

def get_stats(name):
    """Renvoie un dictionnaire de stats
    *name* <str> : nom du joueur
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

####################################################################

async def obs_invoke(f,*args) -> None:
    "appel avec unpacking via l'étoile"
    logging.basicConfig(level=logging.INFO)

    sys.path.append('../')

    host = "localhost"
    port = 4444
    password = ""

    ws = obsws(host, port, password)
    try:
        ws.connect()
        await f(ws,args) # exécution de la fonction
        ws.disconnect()
    except Exception:
        raise OBS_Shutdown("Impossible de se connecter à OBS Studio.")

async def toggle_anim(ws,name) -> None:
    try:
        ws.call(requests.SetSceneItemProperties(scene_name = "Animations", item = name[0], visible = True))
        output_msg(f"L'animation {name} est lancée !")
        await asyncio.sleep(5)
        ws.call(requests.SetSceneItemProperties(scene_name = "Animations", item = name[0], visible = False))

    except KeyboardInterrupt:
        pass

def roll_the_dice(de_a_lancer,bonus,message,valeur_difficulte=0,statistique=""):
    """Permet de lancer un dé, et retourne une chaine formatée indiquant le résultat du jet.
    Effet de bord : envoie une animation sur OBS Studio

    Keywords arguments:
    *de_a_lancer* (int) > valeur de lancer du dé
    *bonus* (int) > bonus à ajouter au dé
    *valeur_difficulte* (int) > valeur à laquelle comparer, si elle existe (par def : 0)
    *message* (discord.message) > objet message discord
    """
    dice = random.randrange(1,(de_a_lancer+1))
    resultat = dice + bonus
    match valeur_difficulte:
        case 0:
            # pas de valeur de difficulté, jet dont on ne connait pas les possibilités de victoire
            if dice == 1:
                quote = "La chance ne vous sourit pas toujours... et ce revers de fortune est cruel !"
                state,anim = "ECHEC CRITIQUE","E_CRIT.avi"
            elif dice == de_a_lancer:
                quote = "Brillant ! Que brûle la flamme, brasier de peur en vos ennemis !"
                state,anim = "REUSSITE CRITIQUE","R_CRIT.avi"
                if(statistique != ""): increase_on_crit(statistique[1:-1],(str(message.author)).split("#")[0])
            else:
                quote = random.choice(["Une progression n'est pas toujours linéaire...","Le pire reste de ne pas savoir que l'on ne sait pas.","L'inconnu, fantasme des savants, plaie des vivants !"])
                state,anim = "INCONNU",""
            string = f"{message.author.mention} > **{state}** {statistique}\n> {dice}/{de_a_lancer} (dé) + {bonus} (bonus) = {resultat}\n> *{quote}*"

        case _:
            # valeur de difficulté existante
            if dice == 1:
                quote = "La chance ne vous sourit pas toujours... et ce revers de fortune est cruel !"
                state,anim = "ECHEC CRITIQUE","E_CRIT.avi"
            elif dice == de_a_lancer:
                quote = "Brillant ! Que brûle la flamme, brasier de peur en vos ennemis !"
                if(statistique != ""): increase_on_crit(statistique,(str(message.author)).split("#")[0])
                state,anim = "REUSSITE CRITIQUE","R_CRIT.avi"
            else:
                if resultat>=valeur_difficulte:
                    quote = random.choice(["Un coup décisif pour la chair comme pour l'esprit !","La voie est claire, le chemin dégagé : ne nous manque plus que la force pour l'emprunter."])
                    state,anim = "REUSSITE","R_STD.avi"
                else:
                    quote = random.choice(["Qui n'avait point prévu ces remuantes choses dans l'ombre ?","La vérité n'éclot jamais du mensonge.","A espoirs illusoires, rêves déchus !"])
                    state,anim = "ECHEC","E_STD.avi"
            string = f"{message.author.mention} > **{state}** {statistique}\n> {dice}/{de_a_lancer} (dé) + {bonus} (bonus) = {resultat} pour une difficulté de {valeur_difficulte}\n> *{quote}*"
    # outputs
    output_msg(string)
    return (string,anim)

def bot(ld):
    client = discord.Client()

    # préparation du dico de stress
    
    listStates,listEffects = [],[]
    with open("resx/stress.csv", newline='') as reader:
        spamreader = csv.reader(reader, delimiter=',', quotechar='"')
        for l in spamreader:
            listStates.append(l[0])
            temp = l[1]
            listEffects.append(temp.replace('"',''))

    # mise en place de l'aide

    helps:dict = {
                    "!support":"pour obtenir de l'aide",
                    "!gennom":"pour générer un nom aléatoire",
                    "!genpnj":"pour générer un PnJ aléatoire",
                    "!linkjdr":"pour récupérer les liens utiles pour les séances",
                    "!linkprojet":"pour obtenir les liens vers les projets",
                    "!dX+Y/Z":"pour lancer un dé à X faces avec un bonus de Y sur une difficulté de Z",
                    "!dX+Y":"pour lancer un dé à X faces avec un bonus de Y sans valeur de difficulté",
                    "!sX":"pour lancer un dé de stress avec un stress de X",
                    "!meow":"Parce qu'il faut forcément un chat !"
                }
        
    help_string = "Vous pouvez utiliser les commandes :\n"
    for key,val in helps.items():
        help_string = help_string + f"\n**{key}** - *{val}*"

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les gens écrire !sup"))
        output_msg(f"JDRBot est prêt !")
        

    @client.event
    async def on_message(message):
        contents:str = message.content

        # nettoyage
        if(contents in ["!disconnect","!support","!gennom","!genpnj","!meow","!linkjdr","!linkprojet","!ad"] or contents[:2] in ["!d","!s","!r"] or contents[:4] in dict_stats.keys()):
            output_msg(f"Réception d'une commande de {str(message.author)} > {contents}")
            messages = await message.channel.history(limit=1).flatten()
            for each_message in messages:
                await each_message.delete()

        match contents:
            case "!ad":
                await message.channel.send("Hey ! C'est partiiiii !")
                e = discord.Embed(title="On est en live maintenant", url="https://www.twitch.tv/tharostv", description="Venez voir tout ce qu'on a pour vous !", color=0xF9BEE4)
                # e.set_thumbnail(url="https://media.discordapp.net/attachments/909452391244525598/939881649066369085/New_Logo_Color4.png")
                await message.channel.send(embed=e)

            case "!linkprojet":

                lembed =    [
                                discord.Embed(title="Youtube principal", url="https://www.youtube.com/channel/UCCn873wDjYSl_YZpNNTbViA", description="Les replays de JdR, les chroniques rôlistes et plein de formats funs", color=0xF9BEE4),
                                discord.Embed(title="Chaine de replays", url="https://www.youtube.com/channel/UCmmNBnYQmZlv6tPz6MO2TNA", description="Retrouvez ici tout ce que vous n'avez pas pu voir en live", color=0xF9BEE4),
                                discord.Embed(title="Streams twitch", url="https://www.twitch.tv/tharostv", description="Pour découvrir tout ce qu'on fait en live", color=0xF9BEE4),
                                discord.Embed(title="Github des projets", url="https://github.com/Tharos-ux", description="Pour récupérer des outils pour vos JdR", color=0xF9BEE4),
                                discord.Embed(title="Cycle de Niathshrubb", url="https://docs.google.com/document/d/1BC4PwwgtKJVfi3yFeJVzcIasZL3iVizx-WNH1jVvk9U/edit?usp=sharing", description="Pour découvrir ce que j'écris !", color=0xF9BEE4)
                            ]

                for e in lembed:
                    await message.channel.send(embed=e)

            case "!linkjdr":

                lembed =    [
                                discord.Embed(title="Règles des JdR", url="https://decorous-ptarmigan-9bf.notion.site/R-gles-JdR-ddd3ac0d4d0c4f98a9b2bcdd0d5cda79", description="Retrouvez ici l'intégralité des règles utilisées pendant les séances !", color=0xF9BEE4),
                                discord.Embed(title="Watch2Gether", url="https://w2g.tv/rooms/i0bpwst6mzv3t9qh9c7?access_key=vivvyyity2uburxwxo4wjm", description="Pour écouter la musique pendant les séances !", color=0xF9BEE4),
                                discord.Embed(title="Utilitaire pour les caméras", url="https://obs.ninja/", description="Pour les flux vidéos, si cela est nécessaire !", color=0xF9BEE4),
                                discord.Embed(title="GDoc du lore", url="https://docs.google.com/document/d/1Ytnvfar50VX2DmUkk1DoovrHz-nE_BAlFBGAkjkNX3Y/edit?usp=sharing", description="Rafraichissez-vous la mémoire quant au lore !", color=0xF9BEE4),
                                discord.Embed(title="Retours de séances", url="https://forms.gle/9nSjZwnFQChf9j546", description="Faites vos retours ici après la fin d'une série de JdR !", color=0xF9BEE4),
                                discord.Embed(title="S'inscrire pour une séance", url="https://forms.gle/TeEFqXFFJvKzvEEE7", description="Inscrivez-vous ici pour participer à une prochaine séance !", color=0xF9BEE4),
                                discord.Embed(title="Manuel de campagne : l'ombre du météore", url="https://decorous-ptarmigan-9bf.notion.site/Manuel-des-joueurs-l-ombre-du-m-t-ore-94bf941c54b54691971558724a154908", description="Par curiosité ou si vous êtes joueurs de la campagne !", color=0xF9BEE4)
                            ]

                for e in lembed:
                    await message.channel.send(embed=e)

            case '!support': 

                await message.channel.send(help_string)

            case "!gennom":

                string = p.Pnj(ld).name
                await message.channel.send(string)

            case "!genpnj":

                monPnj,string = p.Pnj(ld),""
                for key in monPnj.carac:
                    string = string + f"**{key.replace('_',' ')}** = {monPnj.carac[key]}\n"
                await message.channel.send(string)

            case "!meow":

                await message.channel.send(file=discord.File('happy_cat.gif'))
              
            case "!disconnect":

                if(str(message.author.id) == str(admin)):
                    await message.channel.send("Déconnexion du serveur. A bientôt !")

                    client.close()

                    output_msg("PNJMaker est maintenant déconnecté !")

                    exit()

                else:
                    await message.channel.send("Vous n'avez pas les droits pour déconnecter le bot.")

            case _:

                if(contents[:4] in dict_stats.keys()): # dé fonctionnant avec le nom du joueur

                    stat = stat_from_player(dict_stats[contents[:4]],(str(message.author)).split("#")[0])[2:]
                    valeur_difficulte = contents.split("/")[1] if "/" in contents else 0
                    de_a_lancer,bonus = stat.split("+")[0],stat.split("+")[1]

                    output = roll_the_dice(int(de_a_lancer),int(bonus),message,int(valeur_difficulte),f"({dict_stats[contents[:4]]})")

                    asyncio.gather(
                        message.channel.send(output[0]),
                        obs_invoke(toggle_anim,output[1])
                    )

                elif(contents[:2]=='!d'): # dé simple avec ou sans valeur de difficulté

                    datas = contents[2:].replace(" ","") # on nettoie la chaine
                    de_a_lancer,reste = datas.split("+")[0],datas.split("+")[1]

                    diff = reste.split('/')[1] if '/' in reste else 0
                    bonus = reste.split('/')[0] if '/' in reste else reste

                    output = roll_the_dice(int(de_a_lancer),int(bonus),message,int(diff))

                    asyncio.gather(
                        message.channel.send(output[0]),
                        obs_invoke(toggle_anim,output[1])
                    )

                elif(contents[:2]=='!s'): # lancer de dé de stress
                    if (contents[2:]!=''):
                        val_stress:int = int(contents[2:])
                    else:
                        val_stress:int = get_stress((str(message.author)).split("#")[0])

                    dice:int = random.randrange(1,11)
                    index:int = dice + int(val_stress)

                    state,anim = listStates[index],str(listStates[index])[:-2]+".avi"
                    effect = listEffects[index]

                    if(dice >= 8):
                        quote = "La vie n'est que coups au coeur et à l'esprit."
                        increase_on_crit('Stress',(str(message.author)).split("#")[0],1)
                    elif(dice <= 2):
                        quote = "De l'espoir, là même où les plus fous n'auraient su en trouver."
                        increase_on_crit('Stress',(str(message.author)).split("#")[0],-1)
                    else:
                        quote = random.choice(["Maladies de l'esprit sont peste pour la chair !","Pouce par pouce, une seule vérité s'impose à vous : celle du tombeau.","A quoi bon frapper un mal que l'on ne saurait voir ?"])

                    string = f"{message.author.mention} > **{state}**\n> {dice} (dé) : {effect}\n> *{quote}*"

                    output_msg(string)

                    # à tester
                    
                    #coroutine:None = asyncio.ensure_future(obs_invoke,[toggle_anim,anim]) # boucle infinie
                    asyncio.to_thread(obs_invoke,[toggle_anim,anim])
                    await message.channel.send(string)
                    output_msg("Stack vide. Prêt !")


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
    ld = liste_dicos[list(liste_dicos.keys())[0]] if liste_dicos != dict() else l.Loader("data/data.ini")
    bot(ld)

if __name__ == "__main__":
    main()