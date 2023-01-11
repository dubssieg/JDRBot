"Test pour calendrier"
from string import ascii_uppercase
from datetime import datetime, timedelta


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
