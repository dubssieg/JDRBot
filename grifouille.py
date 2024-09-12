"GRIFOUILLE !!!"
from typing import NoReturn
import interactions
from random import randrange, random, choice
from library import load_json, save_json, get_personnas, display_stats, count_crit_values
from pygsheets import authorize
from obs_interactions import obs_invoke, toggle_anim, activate_anim, deactivate_anim
from gsheets_interactions import values_from_player, stat_from_player, increase_on_crit, get_stress, update_char, get_url
from discord_interactions import ScheduledEvents
from time import sleep
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

#############################
### Chargement des tokens ###
#############################

from env.constants import CAL_ID, NO_PINGS_ROLE, PATOUNES_LOVE, PATOUNES_TONGUE, SCOPES, EMOJI_DENY, EMOJI_VALIDATION, URL, DICE_FIELDS, COMPETENCE_POS, COMPETENCES, PERMA_LINKS, W2G_LINK
import pytz

# tokens OBS-WS
tokens_obsws: dict = load_json("obs_ws")
host: str = tokens_obsws["host"]
port: int = tokens_obsws["port"]
password: str = tokens_obsws["password"]

# tokens discord
tokens_connexion: dict = load_json("token")
token_grifouille: str = tokens_connexion['token']
guild_id: int = tokens_connexion['guild_id']
guild_roles: str = tokens_connexion['guild_roles']


# déclaration du client
bot = interactions.Client(
    token=token_grifouille,
    intents=interactions.Intents.GUILD_MEMBERS,
    presence=interactions.ClientPresence(
        status=interactions.StatusType.ONLINE,
        activities=[
            interactions.PresenceActivity(
                name='des pôtichats',
                url=URL,
                emoji=PATOUNES_LOVE,
                type=interactions.PresenceActivityType.STREAMING
            )
        ]
    )
)

# tokens GSheets
gc = authorize(service_file='env/connect_sheets.json')

# datas d'environnement
dict_pos: dict = load_json("pos")  # mapping statistique : position (case)
dict_links: dict = load_json("links")  # liens vers les fiches de persos
dict_bonuses: dict = load_json("bonus")  # stats de résilience
dict_stress: dict = load_json("stress")  # états de stress
quotes: dict = load_json("quotes")  # phrases pour les jets de dés

# préparation du dico de stress
listStates = list(dict_stress.keys())
listEffects = list(dict_stress.values())

stats_choices: list = [interactions.Choice(
    name=val, value=val) for val in dict_pos.keys()]

dice_type: list = [interactions.Choice(
    name=key, value=val) for key, val in DICE_FIELDS.items()]
competence_choices: list = [interactions.Choice(
    name=val, value=val) for val in COMPETENCES]


def init_creditentials_calendar() -> None:
    creds = None
    if os.path.exists("env/token_google_calendar.json"):
        creds = Credentials.from_authorized_user_file(
            "env/token_google_calendar.json", ["https://www.googleapis.com/auth/calendar"])

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "env/credentials_calendar.json", [
                "https://www.googleapis.com/auth/calendar"]
        )
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("env/token_google_calendar.json", "w") as token:
            token.write(creds.to_json())
    print("Calendar token sucessfuly reset")


################ Pour les anniversaires #################


@bot.command(
    name="birthday",
    description="Donnez votre date d'anniversaire pour que le bot vous le souhaite !",
    scope=guild_id,
    options=[
        interactions.Option(
            name="jour",
            description="Jour (1-31) de l'anniversaire",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="mois",
            description="Mois (1-12) de l'anniversaire",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def birthday(ctx: interactions.CommandContext, jour: int, mois: int):
    save_json("birthdays", {**load_json('birthdays'),
              str(ctx.author.mention): f"{jour}.{mois}"})
    await ctx.send(f"Votre anniversaire a été fixé au {jour}.{mois} !", ephemeral=True)


################### Ajout d'un évènement ################

@bot.command(
    name="date",
    description="Ajoute une date dans le calendrier",
    options=[
        interactions.Option(
            name="name",
            description="Nom de l'évènement",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="start",
            description="Temps écrit dans le format DD/MM/YY HH:MM",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="end",
            description="Temps écrit dans le format DD/MM/YY HH:MM",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="long_description",
            description="Longue description textuelle pour définir l'évènement",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="mentions",
            description="Courte description contenant les personnes à mentionner",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def date(
    ctx: interactions.CommandContext,
    name: str,
    start: str,
    end: str,
    long_description: str = 'Un sublime évènement',
    mentions: str = 'Avec de soyeuses personnes'
):
    await ctx.defer()
    if mentions:
        concerned_members: list = list()
        for member in await ctx.guild.get_all_members():
            if str(member.id) in mentions:
                concerned_members.append(member)
        for role in await ctx.guild.get_all_roles():
            if str(role.id) in mentions:
                for member in await ctx.guild.get_all_members():
                    if int(role.id) in member.roles:
                        concerned_members.append(member)

    # Converting dates to desired format
    # Define the Paris timezone
    paris_tz = pytz.timezone('Europe/Paris')

    # Convert start and end times to datetime objects
    start_dt = datetime.strptime(start, '%d/%m/%y %H:%M')
    end_dt = datetime.strptime(end, '%d/%m/%y %H:%M')

    # Localize the datetime objects to Paris timezone
    start_dt = paris_tz.localize(start_dt)
    end_dt = paris_tz.localize(end_dt)

    # Format the datetime objects to the desired string format
    start_date = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_date = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Convert start and end times to UTC timezone
    start_dt_utc = start_dt.astimezone(pytz.utc)
    end_dt_utc = end_dt.astimezone(pytz.utc)

    # Format the datetime objects to the desired string format in UTC
    start_date_utc = start_dt_utc.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_utc = end_dt_utc.strftime("%Y-%m-%dT%H:%M:%S")

    await ScheduledEvents.create_guild_event(
        guild_id=str(ctx.guild_id),
        event_name=name,
        event_description=long_description,
        event_start_time=start_date_utc,
        event_end_time=end_date_utc,
        event_metadata={'location': 'TharosTV'},
    )
    event_id: str = f"https://discord.com/events/313976437818523650/{await ScheduledEvents.find_guild_event(name, 313976437818523650)}"
    if mentions:
        mp_text: str = f"""
Bonjour ! Tu as été notifié(e) sur le serveur **Tharos** [pour un évènement](<{event_id}>).
Merci de **prévenir au plus vite** en cas d'indisponibilité !

*Ce message est automatique, vous pouvez [mettre à jour votre profil](<{guild_roles}>) sur le serveur pour désactiver.* 
    """
        users_to_remind: list = list()
        for member_to_mp in concerned_members:
            if not NO_PINGS_ROLE in member_to_mp.roles:
                try:
                    await member_to_mp.send(mp_text)
                    users_to_remind.append(str(member_to_mp.id))
                except:
                    try:
                        await ctx.author.send(f"Erreur lors de l'envoi de la notification à l'utilisateur {member_to_mp.name} !")
                    except:
                        pass
            else:
                try:
                    await ctx.author.send(f"L'utilisateur {member_to_mp.name} a ses notifications désactivées.")
                except:
                    pass
    creds = Credentials.from_authorized_user_file(
        "env/token_google_calendar.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)

    event = {
        'summary': name,
        'location': 'TharosTV',
        'description': long_description,
        'start': {
            'dateTime': start_date,
            'timeZone': 'Europe/Paris',
        },
        'end': {
            'dateTime': end_date,
            'timeZone': 'Europe/Paris',
        },
        'recurrence': [
        ],
        'attendees': [
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    events_dates: dict = load_json('events')
    events_dates[datetime.strptime(start, '%d/%m/%y %H:%M').strftime("%d-%m-%y")] = events_dates.get(datetime.strptime(start, '%d/%m/%y %H:%M').strftime("%d-%m-%y"), list()) + [
        {
            "title": name,
            "time": datetime.strptime(start, '%d/%m/%y %H:%M').strftime("%H:%M"),
            "people": users_to_remind,
            "url": event_id
        }
    ]
    save_json('events', events_dates)

    event = service.events().insert(calendarId=CAL_ID, body=event).execute()
    print('Event created: ' + event.get('htmlLink'))

    await ctx.send(f"Evènement [**{name}**]({event_id}) créé! {PATOUNES_LOVE}")


################ Pour demander la fiche #################


@ bot.command(
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


def roll_the_dice(message, result_number_of_dices: int, dices: int, faces: int, modificateur: int = 0, valeur_difficulte: int = 0, stat_testee: str = "") -> tuple:
    """Lance un dé dans la stat testée et renvoie le résultat.

    Args:
        message (_type_): _description_
        mode : the type of dice condition to check
        dices : number of dices to roll
        faces (_type_): _description_
        modificateur (int, optional): _description_. Defaults to 0.
        valeur_difficulte (int, optional): _description_. Defaults to 0.
        hero_point (bool, optional): _description_. Defaults to False.
        stat_testee (str, optional): _description_. Defaults to "".

    Returns:
        tuple: chaîne décrivant le résultat et nom de l'anim à envoyer
    """
    # modificateur de résilience
    resilience = dict_bonuses[str(message.author.mention)] if str(
        message.author.mention) in dict_bonuses else 0
    # all_rolls contient tous les jets de dés
    all_rolls: list = [randrange(1, faces) for _ in range(dices)]
    # res contient tous les jets de dés à prendre en compte
    filtered_rolls: list = sorted(all_rolls)[-result_number_of_dices:]
    # values correspond aux jets de dés avec bonus/malus ajoutés
    filtered_rolls_with_modifier: list = [
        val + modificateur + resilience for val in filtered_rolls]
    # stat_testee donne une chaîne pour décrire le jet
    if stat_testee != "":
        if modificateur == 0:
            stat_testee = f"({stat_testee}, {dices}d{faces}, résilience +{resilience})"
        elif modificateur > 0:
            stat_testee = f"({stat_testee}, {dices}d{faces}+{modificateur}, résilience +{resilience})"
        else:
            stat_testee = f"({stat_testee}, {dices}d{faces}-{-modificateur}, résilience +{resilience})"
    # on calcule si le jet est valide ou non
    if valeur_difficulte > 0:
        # si tous les dés sont maximaux, c'est une réussite critique
        if all([val == faces for val in filtered_rolls]):
            dict_bonuses[str(message.author.mention)] = 0
            anim = "R_CRIT.avi"
            str_resultat = f"""
                {message.author.mention} > **REUSSITE CRITIQUE** {stat_testee}
                > Lancers de dés : {', '.join(['**'+str(roll)+'/'+str(faces)+'+'+str(modificateur)+'** ('+str(roll+modificateur)+'+'+str(resilience)+')' for roll in all_rolls])}
                > Difficulté : **{result_number_of_dices}d > {valeur_difficulte-1}**
                > Vos points de résilience sont ramenés à zéro.
                > *{choice(quotes['REUSSITE CRITIQUE'])}*
                """
        # si tous les dés sont minimaux, c'est un échec critique
        elif all([val == 1 for val in filtered_rolls]):
            # On donne un point permanent au joueur
            if stat_testee != "":
                increase_on_crit(
                    str(message.author.mention),
                    dict_links,
                    gc,
                    stat_testee,
                    dict_pos,
                    1
                )
            if "Sang-froid" not in stat_testee:
                anim = "E_CRIT.avi"
                str_resultat = f"""
                    {message.author.mention} > **ECHEC CRITIQUE** {stat_testee}
                    > Lancers de dés : {', '.join(['**'+str(roll)+'/'+str(faces)+'+'+str(modificateur)+'** ('+str(roll+modificateur)+'+'+str(resilience)+')' for roll in all_rolls])}
                    > Difficulté : **{result_number_of_dices}d > {valeur_difficulte-1}**
                    > La compétence {stat_testee} gagne un point !
                    > *{choice(quotes['ECHEC CRITIQUE'])}*
                    """
            else:
                str_resultat, anim = roll_the_stress(
                    message, get_stress(message.author.mention, dict_links, gc))
        # si tous les dés avec bonus/malus sont au-dessus de la valeur de difficulté, c'est une réussite
        elif all([val >= valeur_difficulte for val in filtered_rolls_with_modifier]):
            anim = "R_STD.avi"
            dict_bonuses[str(message.author.mention)] = 0
            str_resultat = f"""
                {message.author.mention} > **REUSSITE** {stat_testee}
                > Lancers de dés : {', '.join(['**'+str(roll)+'/'+str(faces)+'+'+str(modificateur)+'** ('+str(roll+modificateur)+'+'+str(resilience)+')' for roll in all_rolls])}
                > Difficulté : **{result_number_of_dices}d > {valeur_difficulte-1}**
                > Vos points de résilience sont ramenés à zéro.
                > *{choice(quotes['REUSSITE'])}*
                """
        # si tous les dés avec bonus/malus sont en-dessous de la valeur de difficulté, c'est un échec
        else:
            if str(message.author.mention) in dict_bonuses and dict_bonuses[str(message.author.mention)] < 5:
                dict_bonuses[str(message.author.mention)] += 1
            elif str(message.author.mention) not in dict_bonuses:
                dict_bonuses[str(message.author.mention)] = 1
            if "Sang-froid" not in stat_testee:
                anim = "E_STD.avi"
                str_resultat = f"""
                    {message.author.mention} > **ECHEC** {stat_testee}
                    > Lancers de dés : {', '.join(['**'+str(roll)+'/'+str(faces)+'+'+str(modificateur)+'** ('+str(roll+modificateur)+'+'+str(resilience)+')' for roll in all_rolls])}
                    > Difficulté : **{result_number_of_dices}d > {valeur_difficulte-1}**
                    > Vous gagnez un point de résilience.
                    > *{choice(quotes['ECHEC'])}*
                    """
            else:
                str_resultat, anim = roll_the_stress(
                    message, get_stress(message.author.mention, dict_links, gc))
    # si on a pas de valeur de difficulté, on ne dit rien
    else:
        anim = "INCONNU.avi"
        str_resultat = f"""
            {message.author.mention} > **INCONNU** {stat_testee}
            > Lancers de dés : {', '.join(['**'+str(roll)+'/'+str(faces)+'+'+str(modificateur)+'** ('+str(roll+modificateur)+')' for roll in all_rolls])}
            > *{choice(quotes['INCONNU'])}*
            """
    save_json('bonus', dict_bonuses)
    return (str_resultat, anim)


@bot.command(
    name="caracteristique",
    description="Permet de changer une valeur sur votre fiche de stats.",
    scope=guild_id,
    options=[
        interactions.Option(
            name="competence",
            description="Caractéristique à modifier !",
            type=interactions.OptionType.STRING,
            choices=competence_choices,
            required=True,
        ),
        interactions.Option(
            name="ajouter",
            description="Nombre à ajouter à la caractéristique",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="soustraire",
            description="Nombre à soustraire à la caractéristique",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="fixer",
            description="Nombre auquel fixer la caractéristique",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
    ],
)
async def caracteristique(ctx: interactions.CommandContext, competence: str, ajouter=None, soustraire=None, fixer=None):
    if not (ajouter is None and soustraire is None and fixer is None):
        await ctx.defer()

        values = values_from_player(ctx.author.mention, dict_links, gc)
        labels: list = list(values.keys())
        valeurs_max: list = [values[label]['valeur_max']
                             for label in labels]
        valeurs_actuelle: list = [values[label]
                                  ['valeur_actuelle'] for label in labels]
        valeurs_critique: list = [values[label]
                                  ['seuil_critique'] for label in labels]
        nb_val_critique, zero_stats = count_crit_values(
            valeurs_actuelle, valeurs_critique)

        print(values)

        pos: int = labels.index(competence)
        if fixer is not None:
            future_value: int = max(min(fixer, valeurs_max[pos]), 0)
        else:
            future_value: int = valeurs_actuelle[pos]
        if ajouter is not None:
            future_value = min(future_value + ajouter, valeurs_max[pos])
        if soustraire is not None:
            future_value = max(future_value-soustraire, 0)

        update_char(ctx.author.mention, dict_links, gc, COMPETENCE_POS, competence,
                    future_value)

        values = values_from_player(ctx.author.mention, dict_links, gc)
        labels: list = values.keys()
        new_valeurs: list = [values[label]
                             ['valeur_actuelle'] for label in labels]
        new_critique: list = [values[label]
                              ['seuil_critique'] for label in labels]
        new_count, new_zero = count_crit_values(new_valeurs, new_critique)
        if new_count > nb_val_critique or new_zero > zero_stats:
            # si il y a un changement d'état, qui empire
            if new_count >= 3 or new_zero >= 2:
                await obs_invoke(toggle_anim, host, port, password, "Mort.avi")
            elif new_count <= 2 or new_zero == 1:
                await obs_invoke(toggle_anim, host, port, password, "Portes_Mort.avi")
        await ctx.send(f"La valeur de **{competence}** de {ctx.author.mention} a été changée de **{valeurs_actuelle[pos]}** à **{future_value}** !\nTu as {new_count} valeurs en dessous du seuil critique, dont {new_zero} valeurs à zéro.")


@bot.command(
    name="music",
    description="Renvoie le lien du salon Watc2Gether pour les parties de jeu de rôle.",
    scope=guild_id,
)
async def link(ctx: interactions.CommandContext):
    await ctx.send(f"Voici le lien du [**salon pour la musique**](<{W2G_LINK}>) ! {PATOUNES_LOVE}", ephemeral=True)


@bot.command(
    name="link",
    description="Renvoie le lien vers la fiche personnage liée, ou un message si aucune fiche n'est liée.",
    scope=guild_id,
)
async def link(ctx: interactions.CommandContext):
    try:
        await ctx.send(f"Voici le lien de [**ta fiche personnage liée**](<{get_url(ctx.author.mention, dict_links, gc)}>) ! {PATOUNES_LOVE}", ephemeral=True)
    except Exception:
        await ctx.send("Désolé, tu ne semble pas avoir de fiche liée. N'hésite pas à en lier une avec **/save_file** !", ephemeral=True)


@bot.command(
    name="display",
    description="Affiche les statistiques actuelles de la fiche active.",
    scope=guild_id,
)
async def display(ctx: interactions.CommandContext):
    await ctx.defer()
    try:
        values = values_from_player(ctx.author.mention, dict_links, gc)
        labels: list = list(values.keys())
        valeurs_max: list = [values[label]['valeur_max'] for label in labels]
        valeurs_actuelle: list = [values[label]
                                  ['valeur_actuelle'] for label in labels]
        valeurs_critique: list = [values[label]
                                  ['seuil_critique'] for label in labels]
        path: str = display_stats(
            labels, valeurs_actuelle, valeurs_max, valeurs_critique)
        crit, zero = count_crit_values(valeurs_actuelle, valeurs_critique)
        await interactions.ext.files.command_send(ctx, f"Voici les stats actuelles de {ctx.author.mention}.\nTu as {crit} valeurs en dessous du seuil critique, dont {zero} valeurs à zéro.", files=interactions.File(filename=path))

    except ConnectionError:
        message = ConnectionError(
            f"Impossible d'atteindre la fiche pour {ctx.author.mention}.")
    except ValueError:
        message = ValueError(
            f"Désolé {ctx.author.mention}, tu ne sembles pas avoir de fiche liée dans ma base de données.")


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
            name="number_dice",
            description="Nombre de dés devant atteindre la valeur de difficulté",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
    ],
)
async def stat(ctx: interactions.CommandContext, charac: str, number_dice: int = 1, valeur_difficulte: int = -1, point_heroisme: bool = False):
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
        stats_of_player = stat_from_player(
            ctx.author.mention, dict_links, gc, charac)
        dices, remain = stats_of_player.split('D')
        values = remain.split('+')
        message, anim = roll_the_dice(
            message=ctx,
            result_number_of_dices=number_dice,
            dices=int(dices),
            faces=int(float(values[0].replace(',', '.'))),
            modificateur=int(values[1]),
            valeur_difficulte=valeur_difficulte,
            stat_testee=charac)
        await obs_invoke(deactivate_anim, host, port, password, anim)
    except ConnectionError:
        message = ConnectionError(
            f"Impossible d'atteindre la valeur de {charac} pour {ctx.author.mention}.")
    except ValueError:
        message = ValueError(
            f"Désolé {ctx.author.mention}, tu ne sembles pas avoir de fiche liée dans ma base de données.")
    finally:
        await ctx.send(str(message))
        try:
            await obs_invoke(activate_anim, host, port, password, anim)
        except:
            pass


def roll_the_stress(message, val_stress, player_has_file: bool = True):
    """
    Lance un dé de stress et en traite les conséquences

    Keywords arguments:
    *message* (discord.message) > source de la commande
    *val_stress* (str) > valeur du stress indiqué dans le message
    *player_has_file* (bool) > si le joueur a une fiche qui lui est associée
    """
    if player_has_file:
        val_max: int = 10
    else:
        val_max: int = 30
    dice: int = randrange(1, val_max)
    index: int = dice + int(val_stress)
    state, anim = listStates[index], str(
        listStates[index])[:-2]+".avi"
    effect = listEffects[index]

    if (dice >= 0.8*val_max):
        "Effet de stress négatif"
        quote = choice(quotes["STRESS NEGATIF"])
        if player_has_file:
            increase_on_crit(str(message.author.mention),
                             dict_links, gc, 'Stress', dict_pos,  1)
    elif (dice <= 0.2*val_max):
        "Effet de stress positif"
        quote = choice(quotes["STRESS POSITIF"])
        if player_has_file:
            increase_on_crit(str(message.author.mention),
                             dict_links, gc, 'Stress', dict_pos,  -1)
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
    except:
        try:
            message, anim = roll_the_stress(ctx, 0, False)
        except ConnectionError:
            message = ConnectionError(
                f"Impossible d'atteindre la valeur de stress pour {ctx.author.mention}.")
        except ValueError:
            message = ValueError(
                f"Désolé {ctx.author.mention}, tu ne sembles pas avoir de fiche liée dans ma base de données.")
    finally:
        await ctx.send(str(message))


@bot.command(
    name="dice",
    description="Simule un dé à n faces !",
    scope=guild_id,
    options=[
        interactions.Option(
            name="dices",
            description="Nombre de dés à lancer",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
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
            name="number_dice",
            description="Nombre de dés devant atteindre la valeur de difficulté",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
    ],
)
async def dice(ctx: interactions.CommandContext, dices: int = 1, faces: int = 20, modificateur: int = 0, valeur_difficulte: int = -1, number_dice: int = 1):
    await ctx.defer()
    message, anim = roll_the_dice(
        message=ctx,
        result_number_of_dices=number_dice,
        dices=dices,
        faces=faces,
        modificateur=modificateur,
        valeur_difficulte=valeur_difficulte
    )
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

################ Pour récupérer le lien de caméra #################


@bot.command(
    name="camera",
    description="Renvoie le lien permanent qui vous est assigné pour les caméras.",
    scope=guild_id,
)
async def toss(ctx: interactions.CommandContext) -> None:
    answer: str | None = None
    for id_role, link in PERMA_LINKS.items():
        if id_role in ctx.author.roles:
            answer = link
    if answer:
        await ctx.send(f"Voici le lien vers ton [**slot caméra**](<{answer}>) !", ephemeral=True)
    else:
        await ctx.send(f"Tu n'as pas de caméra assignée, contacte un admin !", ephemeral=True)


################ Pour effectuer des sondages #################


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
        interactions.Option(
            name="description",
            description="Texte de description pour donner des détails.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="mentions",
            description="Texte afin de mentionner des rôles.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def calendar(ctx: interactions.CommandContext, duree: int = 7, delai: int = 0, titre: str = "Date pour la prochaine séance !", description: str = 'Un sublime calendrier', mentions: str = 'Avec de sublimes personnes') -> None:
    """Crée un calendrier sous forme d'embed, pour faire un sondage sur les jours suivants

    Args:
        ctx (interactions.CommandContext): contexte de la commande
        days (int, optional): Période de temps sur laquelle s'étend le sondage. Defaults to 7.
        offset (int, optional): Décalage en jours. Defaults to 0.
        description (str, optional): Un titre pour le sondage. Defaults to "Date pour la prochaine séance !".
    """
    await ctx.defer()
    if mentions:
        concerned_members: list = list()
        for member in await ctx.guild.get_all_members():
            if str(member.id) in mentions:
                concerned_members.append(member)
        for role in await ctx.guild.get_all_roles():
            if str(role.id) in mentions:
                for member in await ctx.guild.get_all_members():
                    if int(role.id) in member.roles:
                        concerned_members.append(member)
    nb_jours: int = duree if duree <= 12 and duree > 0 else 7
    decalage: int = delai if delai >= 0 else 0
    list_days: list = ["Lundi", "Mardi", "Mercredi",
                       "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    list_letters: list = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9", "\U0001F1EA", "\U0001F1EB", "\U0001F1EC", "\U0001F1ED",
                          "\U0001F1EE", "\U0001F1EF", "\U0001F1F0", "\U0001F1F1", "\U0001F1F2", "\U0001F1F3", "\U0001F1F4", "\U0001F1F5", "\U0001F1F6", "\U0001F1F7"]
    liste_jours: list = list()

    # on itère à travers les jours
    for step, day in enumerate(range(1, nb_jours+1, 1)):
        future = datetime.today().replace(hour=20, minute=45, second=0,
                                          microsecond=0) + timedelta(days=day+decalage)
        liste_jours.append(
            f"{list_letters[step]}  {list_days[future.weekday()]} {future.day}.{future.month} (20:45)")
    # on définit une lise d'emoji de la longueur du nombre de réponses possibles
    list_emoji: list = [list_letters[i]
                        for i in range(step+1)] + [EMOJI_VALIDATION] + [EMOJI_DENY]

    information: str = f"*Merci de répondre au plus vite !*\n*Après avoir voté, cliquez sur *{EMOJI_VALIDATION}\n*Aucune date ne convient ? Cliquez sur *{EMOJI_DENY}"

    if description:
        embed = interactions.Embed(
            title=titre, description=f"{description}\n\n{information}", color=0xC2E9AA)
    else:
        embed = interactions.Embed(
            title=titre, footer=information, color=0xC2E9AA)

    for key in liste_jours:
        embed.add_field(name=f"{key}", value="", inline=False)

    if mentions:
        message = await ctx.send(mentions, embeds=embed)
        mp_text: str = f"""
Bonjour ! Tu as été notifié(e) sur le serveur **Tharos** pour un sondage. Merci d'y répondre quand tu pourras !
## {titre} ({message.url})
> {description}

*Ce message est automatique, vous pouvez [mettre à jour votre profil](<{guild_roles}>) sur le serveur pour désactiver.* 
    """
        for member_to_mp in concerned_members:
            if not NO_PINGS_ROLE in member_to_mp.roles:
                try:
                    await member_to_mp.send(mp_text)
                except:
                    try:
                        await ctx.author.send(f"Erreur lors de l'envoi de la notification à l'utilisateur {member_to_mp.name} !")
                    except:
                        pass
            else:
                try:
                    await ctx.author.send(f"L'utilisateur {member_to_mp.name} a ses notifications désactivées.")
                except:
                    pass
    else:
        message = await ctx.send(embeds=embed)

    # affiche les réactions pour le sondage
    for emoji in list_emoji:
        await message.create_reaction(emoji)


@ bot.command(
    name="poll",
    description="Crée un sondage simple à deux options",
    scope=guild_id,
    options=[
        interactions.Option(
            name="titre",
            description="Texte de titre du sondage.",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="mentions",
            description="Petit texte en-dessous pour mentionner des rôles, ou donner des détails.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def poll(ctx: interactions.CommandContext, titre: str, mentions: str | None = None) -> None:
    await ctx.defer()
    if mentions:
        concerned_members: list = list()
        for member in await ctx.guild.get_all_members():
            if str(member.id) in mentions:
                concerned_members.append(member)
        for role in await ctx.guild.get_all_roles():
            if str(role.id) in mentions:
                for member in await ctx.guild.get_all_members():
                    if int(role.id) in member.roles:
                        concerned_members.append(member)

    list_emoji: list = [EMOJI_VALIDATION, EMOJI_DENY]

    if mentions is not None:
        embed = interactions.Embed(
            title=titre, description=mentions, color=0xC2E9AA)
    else:
        embed = interactions.Embed(
            title=titre, color=0xC2E9AA)

    poll_embed = {
        f'{EMOJI_VALIDATION} - La proposition me convient !': "Si elle ne vous convient qu'avec des réserves, sentez-vous libres de les exprimer en réponse.",
        f'{EMOJI_DENY} - La proposition ne me convient pas': "Merci de valider que vous avez lu, et, le cas échéant, préciser votre pensée"
    }

    for key, value in poll_embed.items():
        embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    information: str = f"Merci de répondre au plus vite ! {PATOUNES_TONGUE}"

    message = await ctx.send(information, embeds=embed)
    if mentions:
        mp_text: str = f"""
Bonjour ! Tu as été notifié(e) sur le serveur **Tharos** pour un sondage. Merci d'y répondre quand tu pourras !
## {titre} ({message.url})
> {mentions}

*Ce message est automatique, vous pouvez [mettre à jour votre profil](<{guild_roles}>) sur le serveur pour désactiver.* 
    """
        for member_to_mp in concerned_members:
            if not NO_PINGS_ROLE in member_to_mp.roles:
                try:
                    await member_to_mp.send(mp_text)
                except:
                    try:
                        await ctx.author.send(f"Erreur lors de l'envoi de la notification à l'utilisateur {member_to_mp.name} !")
                    except:
                        pass
            else:
                try:
                    await ctx.author.send(f"L'utilisateur {member_to_mp.name} a ses notifications désactivées.")
                except:
                    pass
    # affiche les réactions pour le sondage
    for emoji in list_emoji:
        await message.create_reaction(emoji)


def main() -> NoReturn:
    "Main loop for Grifouille"
    init_creditentials_calendar()
    while (True):
        try:
            bot.load('interactions.ext.files')
            bot.start()
        except KeyboardInterrupt:
            print(KeyboardInterrupt("Keyboard interrupt, terminating Grifouille"))
            break
        except Exception as exc:
            print(exc)
            sleep(10)


if __name__ == "__main__":
    main()
