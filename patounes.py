"PATOUNES !!!"
from sys import path
from time import sleep
from typing import NoReturn
from discord.ext import commands, tasks
from discord import Streaming, FFmpegPCMAudio, Intents, ClientException
from pygsheets import authorize
from library import output_msg, load_json, YTDLSource
from datetime import date, datetime

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

############################## DEF BOT ##################################

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

############################## DEF BOT ##################################


@bot.event
async def on_ready() -> None:
    "Lorsque le bot se connecte, effectue des actions d'initialisation"
    await bot.change_presence(activity=Streaming(
        name="des pôtichats", url="https://www.twitch.tv/TharosTV"
    ))
    birthday.start()
    output_msg("PATOUNES EST PRET !")


@tasks.loop(minutes=60)
async def birthday():
    for people, date_birthday in load_json('birthdays').items():
        day, month = date_birthday.split('.')
        if date.today().day == int(day) and date.today().month == int(month) and datetime.now().hour == 9:
            for guild in bot.guilds:
                if str(guild.id) == "313976437818523650":
                    for channel in guild.channels:
                        if str(channel.id) == "313977728242155520":
                            await channel.send(f"Hey, c'est l'anniversaire de {people} ! <:patounes_heart:979510606216462416>")


@bot.command()
@commands.has_permissions(administrator=True)
async def play(ctx, url: str) -> None:
    "Télécharge et joue une musique via un vocal discord"
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(  # type: ignore
                url, loop=bot.loop)
            bot.loop.create_task(play_source(voice_channel, filename))
            await ctx.send(f'**Joue :** <{url}>')
    except ClientException as exc:
        await ctx.send("Désolé, le bot n'est pas connecté <:patounes_sad:979501604552212490>")
    finally:
        await ctx.delete()


async def play_source(voice_client, filename: str):
    "Play in loop a sound"
    source: FFmpegPCMAudio = FFmpegPCMAudio(
        executable="ffmpeg", source=filename)
    voice_client.play(source, after=lambda e: print(
        e) if e else bot.loop.create_task(play_source(voice_client, filename)))


@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Désolé, tu ne disposes pas des privilèges pour exécuter cette commande <:patounes_sad:979501604552212490>")


@bot.command()
@commands.has_permissions(administrator=True)
async def stop(ctx):
    "Demande au bot de stopper la musique"
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Le bot ne joue rien actuellement <:patounes_sad:979501604552212490>")
    await ctx.delete()


@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Désolé, tu ne disposes pas des privilèges pour exécuter cette commande <:patounes_sad:979501604552212490>")


@bot.command()
@commands.has_permissions(administrator=True)
async def fetch(ctx, url):
    "Demande au bot de pré-télécharger une musique"
    async with ctx.typing():
        _ = await YTDLSource.from_url(url, loop=bot.loop)  # type: ignore
        await ctx.send(f'**Téléchargé avec succès :** {url}')
    await ctx.delete()


@fetch.error
async def fetch_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Désolé, tu ne disposes pas des privilèges pour exécuter cette commande <:patounes_sad:979501604552212490>")


@bot.command()
@commands.has_permissions(administrator=True)
async def join(ctx):
    "Demande au bot de rejoindre le vocal"
    if not ctx.message.author.voice:
        await ctx.send("Désolé, tu n'es pas dans un chan vocal <:patounes_sad:979501604552212490>")
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    ctx.delete()


@join.error
async def join_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Désolé, tu ne disposes pas des privilèges pour exécuter cette commande <:patounes_sad:979501604552212490>")


@bot.command()
@commands.has_permissions(administrator=True)
async def leave(ctx):
    "Demande au bot de quitter le vocal"
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Désolé, le bot est déjà déconnecté <:patounes_sad:979501604552212490>")
    await ctx.delete()


@leave.error
async def leave_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Désolé, tu ne disposes pas des privilèges pour exécuter cette commande <:patounes_sad:979501604552212490>")


def main() -> NoReturn:
    "Main loop for Patounes"
    path.append('../')
    while (True):
        try:
            bot.run(token)
        except KeyboardInterrupt:
            print(KeyboardInterrupt("Keyboard interrupt, terminating Grifouille"))
            exit(0)
        except Exception as exc:
            print(exc)
            sleep(10)


if __name__ == "__main__":
    main()
