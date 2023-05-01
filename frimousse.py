"FRIMOUSSE !!!"
import asyncio
from typing import NoReturn
from time import sleep
from json import load
from datetime import datetime, timedelta
from interactions import Embed, Client, Status, Activity, ActivityType, Modal, SlashContext, ShortText, ParagraphText, slash_command, ModalContext
from obs_interactions import obs_invoke, toggle_filter

#############################
### Chargement des tokens ###
#############################

# tokens discord
tokens_connexion: dict = load(
    open("env/token_frimousse.json", "r", encoding='utf-8'))
token_grifouille: str = tokens_connexion['token']
guild: int = tokens_connexion['guild_id']

# déclaration du client
bot = Client(
    token=token_grifouille,
    status=Status.ONLINE,
    activity=Activity(
        name="des pôtichats",
        type=ActivityType.STREAMING,
        url="https://www.twitch.tv/TharosTV",
    )
)

patounes_love: str = "<:patounes_heart:979510606216462416>"
patounes_tongue: str = "<:patounes_tongue:979488514561421332>"
emoji_validation: str = "<:patounes_yes:979516938231361646>"
emoji_deny: str = "<:patounes_no:979517886961967165>"


# listes utiles à déclarer en amont
list_letters: list = [
    "\U0001F1E6",
    "\U0001F1E7",
    "\U0001F1E8",
    "\U0001F1E9",
    "\U0001F1EA",
    "\U0001F1EB",
    "\U0001F1EC",
    "\U0001F1ED",
    "\U0001F1EE",
    "\U0001F1EF",
    "\U0001F1F0",
    "\U0001F1F1",
    "\U0001F1F2",
    "\U0001F1F3",
    "\U0001F1F4",
    "\U0001F1F5",
    "\U0001F1F6",
    "\U0001F1F7"
]


list_days: list = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche"
]


@slash_command(
    name="slash_test",
    description="Fonction de test !",
)
async def slash_test(ctx: SlashContext):
    "Teste une commande"
    await ctx.defer()
    name_tags: dict = {
        'MJ': {'chan': None, 'mute': False},
        'Joueur1':  {'chan': None, 'mute': False},
        'Joueur2':  {'chan': None, 'mute': False},
        'Joueur3':  {'chan': None, 'mute': False},
        'Joueur4':  {'chan': None, 'mute': False},
        'Joueur5':  {'chan': None, 'mute': False}
    }
    for tag in name_tags:
        await obs_invoke(
            toggle_filter, 'localhost', '4444', 'coucou', f"Cam_{tag}", [
                'AFK_SAT', 'AFK_BLUR'], True
        )
    await ctx.send(f"FRIMOUSSE EST PRET !")


@slash_command(
    name="calendrier",
    description="Crée un sondage de disponibilités"
)
async def calendrier(ctx: SlashContext) -> None:
    """Crée un calendrier sous forme d'embed, pour faire un sondage sur les jours suivants

    Args:
        ctx (interactions.CommandContext): contexte de la commande
        days (int, optional): Période de temps sur laquelle s'étend le sondage. Defaults to 7.
        offset (int, optional): Décalage en jours. Defaults to 0.
        description (str, optional): Un titre pour le sondage. Defaults to "Date pour la prochaine séance !".
    """
    calendar_modal: Modal = Modal(
        ShortText(
            label="Choisis le titre du calendrier",
            custom_id="titre",
            placeholder="Calendrier pour la prochaine séance !"
        ),
        ParagraphText(
            label="Ajoute une description au calendrier",
            custom_id="description",
            required=False
        ),
        ShortText(
            label="Choisis la durée en jours du calendrier",
            custom_id="temps",
            placeholder="7"
        ),
        ShortText(
            label="Nombre de jours avant le début",
            custom_id="delai",
            placeholder="0"
        ),
        title="Créer un sondage",
    )
    await ctx.send_modal(
        modal=calendar_modal
    )

    try:
        # Parsing de la modal
        return_modal: ModalContext = await bot.wait_for_modal(
            modal=calendar_modal,
            author=ctx.author.id,
            timeout=120)
    except asyncio.TimeoutError:
        # Trop long temps de réponse
        return await ctx.send("Tu as pris plus de deux minutes pour répondre !", ephemeral=True)
    titre: str | None = return_modal.responses.get('titre')
    mentions: str | None = return_modal.responses.get('description')
    duree = return_modal.responses.get('temps')
    if duree is None or not duree.isdigit():
        duree = 7
    else:
        duree = int(duree)
    delai = return_modal.responses.get('delai')
    if delai is None or not delai.isdigit():
        delai = 0
    else:
        delai = int(delai)

    nb_jours: int = duree if duree <= 12 and duree > 0 else 7
    decalage: int = delai if delai >= 0 else 0
    liste_jours: dict = dict()
    step: int = 0

    # on itère à travers les jours
    for day in range(1, nb_jours+1, 1):
        future = datetime.today() + timedelta(days=day+decalage)
        horaire: str | list = [
            "Rassemblement **9h45**, début 10h !",
            "Rassemblement **13h45**, début 14h !",
            "Rassemblement **20h45**, début 21h !"
        ] if future.weekday(
        ) >= 5 else "Rassemblement **20h45**, début 21h !"
        if isinstance(horaire, list):
            for h in horaire:
                liste_jours[f"{list_letters[step]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = h
                step += 1
        else:
            liste_jours[f"{list_letters[step]} - {list_days[future.weekday()]} {future.day}.{future.month}"] = horaire
            step += 1

    # on définit une lise d'emoji de la longueur du nombre de réponses possibles
    list_emoji: list = [list_letters[i]
                        for i in range(step)] + [emoji_validation] + [emoji_deny]

    # role = await interactions.get(bot, interactions.Role, object_id=ROLE_ID, parent_id=GUILD_ID) ajouter à embed.description les rôles à tag , avec champ de liste ?
    if mentions is not None:
        embed = Embed(
            title=titre,
            description=mentions,
            color=0xC2E9AA
        )
    else:
        embed = Embed(
            title=titre,
            color=0xC2E9AA
        )

    for key, value in liste_jours.items():
        embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    information: str = f"Merci de répondre au plus vite !\nAprès avoir voté, cliquez sur {emoji_validation}\nSi aucune date ne vous convient, cliquez sur {emoji_deny}"

    message = await ctx.send(information, embeds=embed)
    # affiche les réactions pour le sondage
    for emoji in list_emoji:
        await message.add_reaction(emoji)


@slash_command(
    name="poll",
    description="Crée un sondage simple à deux options",
)
async def poll(ctx: SlashContext):
    "Sondage simple"
    poll_modal: Modal = Modal(
        ShortText(
            label="Choisis le titre du sondage",
            custom_id="titre"
        ),
        ParagraphText(
            label="Ajoute une description au sondage",
            custom_id="description"
        ),
        title="Créer un sondage",
    )
    await ctx.send_modal(
        modal=poll_modal
    )

    try:
        # Parsing de la modal
        return_modal: ModalContext = await bot.wait_for_modal(
            modal=poll_modal,
            author=ctx.author.id,
            timeout=120)
    except asyncio.TimeoutError:
        # Trop long temps de réponse
        return await ctx.send("Tu as pris plus de deux minutes pour répondre !", ephemeral=True)
    titre: str | None = return_modal.responses.get('titre')
    mentions: str | None = return_modal.responses.get('description')

    list_emoji: list = [emoji_validation, emoji_deny]

    if mentions is not None:
        embed = Embed(
            title=titre,
            description=mentions,
            color=0xC2E9AA
        )
    else:
        embed = Embed(
            title=titre,
            color=0xC2E9AA
        )

    poll_embed = {f'{emoji_validation} - Je suis intéressé.e !': "La date sera déterminée ultérieurement",
                  f'{emoji_deny} - Je ne souhaite pas participer': "Merci de cliquer pour montrer que vous avez lu"}

    for key, value in poll_embed.items():
        embed.add_field(name=f"{key}", value=f"{value}", inline=False)

    information: str = f"Merci de répondre au plus vite ! {patounes_tongue}"

    message = await ctx.send(
        information,
        embeds=embed
    )
    # affiche les réactions pour le sondage
    for emoji in list_emoji:
        await message.add_reaction(emoji)


def main() -> NoReturn:
    "Main loop for Frimousse"
    while (True):
        try:
            bot.start()
        except KeyboardInterrupt:
            print(KeyboardInterrupt("Keyboard interrupt, terminating Frimousse"))
            exit(0)
        except Exception as exc:
            print(exc)
            sleep(10)


if __name__ == "__main__":
    main()
