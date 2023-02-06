"PATOUNES !!!"
from sys import path
from discord.ext import commands
from discord import Client, Streaming, FFmpegPCMAudio, Intents, ClientException
from pygsheets import authorize
from lib import output_msg, load_json, YTDLSource
from obs_interactions import toggle_filter, obs_invoke

##################### TOKENS DE CONNEXION ##########################

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

name_tags: dict = {
    'MJ': {'chan': None, 'mute': False},
    'Joueur1':  {'chan': None, 'mute': False},
    'Joueur2':  {'chan': None, 'mute': False},
    'Joueur3':  {'chan': None, 'mute': False},
    'Joueur4':  {'chan': None, 'mute': False},
    'Joueur5':  {'chan': None, 'mute': False}
}

############################## DEF BOT ##################################

intents = Intents().all()
client = Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

############################## DEF BOT ##################################


async def delete_command(message) -> None:
    "Supprime le message à l'origine de la commande"
    messages = await message.channel.history(limit=1).flatten()
    for each_message in messages:
        await each_message.delete()


async def send_texte(chaine: str, source, kwargs: dict | None = None):
    """
    Envoie le message {chaine} dans le chan de la commande
    Les kwargs peuvent contenir
        file: File = ...
        embed: Embed = ...
    """
    if kwargs is None:
        await source.channel.send(chaine)
    else:
        await source.channel.send(chaine, **kwargs)


@bot.event
async def on_ready() -> None:
    "Lorsque le bot se connecte, effectue des actions d'initialisation"
    await bot.change_presence(activity=Streaming(
        name="des pôtichats", url="https://www.twitch.tv/TharosTV"
    ))
    for tag in name_tags:
        try:
            await obs_invoke(
                toggle_filter, host, port, password, f"Cam_{tag}", [
                    'AFK_SAT', 'AFK_BLUR'], True
            )
        except ConnectionError as exc:
            print(exc)
    output_msg("PATOUNES EST PRET !")


@bot.command(name='play', help='Envoyer de la bonne zik via Patounes')
async def play(ctx, url: str) -> None:
    "Télécharge et joue une musique via un vocal discord"
    await delete_command(ctx.message)
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(  # type: ignore
                url, loop=bot.loop)
            voice_channel.play(FFmpegPCMAudio(
                executable="ffmpeg", source=filename))
            await send_texte(f'**Joue :** <{url}>', ctx.message)
    except ClientException as exc:
        print(exc)
        await send_texte("Désolé, le bot n'est pas connecté :(", ctx.message)


@bot.command(name='stop', help='Arrête la musique')
async def stop(ctx):
    "Demande au bot de stopper la musique"
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await send_texte("Le bot ne joue rien actuellement.", ctx.message)


@bot.command(name='fetch', help='Pré-télécharge une musique')
async def fetch(ctx, url):
    "Demande au bot de pré-télécharger une musique"
    await delete_command(ctx.message)
    async with ctx.typing():
        _ = await YTDLSource.from_url(url, loop=bot.loop)
        await send_texte(f'**Téléchargé avec succès :** {url}', ctx.message)


@bot.command(name='join', help='Demander à Patounes de rejoindre un vocal')
async def join(ctx):
    "Demande au bot de rejoindre le vocal"
    await delete_command(ctx.message)
    if not ctx.message.author.voice:
        await send_texte("Désolé, tu n'es pas dans un chan vocal :(", ctx.message)
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='Demander à Patounes de quitter un vocal')
async def leave(ctx):
    "Demande au bot de quitter le vocal"
    await delete_command(ctx.message)
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await send_texte("Désolé, le bot est déjà déconnecté :(", ctx.message)


@bot.event
async def on_voice_state_update(member, _, after):
    """Regarde ce que l'utilisateur fait du vocal ; si il est mute,
    ou dans un chan différent du MJ, met un effet sur sa caméra !

    Args:
        member : le membre qui vient d'effectuer une action sur le vocal
        before : état du vocal avant changement
        after : état du vocal après changement
    """
    roles = [str(role.name) for role in member.roles]
    for tag, values in name_tags.items():
        if tag in roles:
            try:
                values['chan'] = after.channel.id
            except AttributeError:
                values['chan'] = None
            values['mute'] = after.self_mute
    for tag_name, infos in name_tags.items():
        try:
            await obs_invoke(toggle_filter, host, port, password, f"Cam_{tag_name}",
                             ['AFK_SAT', 'AFK_BLUR'],
                             infos['chan'] != name_tags['MJ']['chan'] or infos['mute'])
        except ConnectionError as exc:
            print(exc)


if __name__ == "__main__":
    path.append('../')
    bot.run(token)
