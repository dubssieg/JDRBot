import interactions
"Tentative pour record en continu vers local et écoute du flux"
# requires interactions v5
# pip uninstall interactions
# pip install git+https://github.com/interactions-py/interactions.py.git@5.x

"""
Idée complète : mapping rôles-personnes
> le mapping contrôle les caméras + le déclenchement des switchs

> si la personne parle, 
> (optionnel) s'en servir pour root l'audio dans OBS? peut-on récup chaque caméra par ce biais ?
"""


@interactions.component_callback("start_recording")
async def start_recording(ctx):
    if not ctx.voice_state:
        vc = ctx.author.voice.channel
        await vc.connect()

    vc = ctx.voice_state
    await vc.start_recording()  # default encoding is `mp3`
    recording_status.restart()

    await ctx.send("Started recording!", ephemeral=True)


@interactions.component_callback("stop_recording")
async def stop_recording(ctx):
    await ctx.defer()
    recorder = ctx.voice_state.recorder
    await recorder.stop_recording()

    await ctx.send(
        "Stopped recording!",
        files=[
            File(file, file_name=f"recording_{user_id}.{recorder.encoding}")
            for user_id, file in recorder.output.items()
        ],
    )


@slash_command("record-prompt")
async def record(ctx):
    await ctx.send(
        "Click the button to start recording!",
        components=[
            interactions.Button(
                custom_id="start_recording", label="Start Recording", style=interactions.ButtonStyle.PRIMARY
            ),
            interactions.Button(
                custom_id="stop_recording", label="Stop Recording", style=interactions.ButtonStyle.DANGER
            ),
        ],
    )
