"Recording implementation that has an altered comportement on record"
from interactions import component_callback, Button, slash_command, File, ButtonStyle


@component_callback("start_recording")
async def start_recording(ctx):
    if not ctx.voice_state:
        vc = ctx.author.voice.channel
        await vc.connect()

    vc = ctx.voice_state
    await vc.start_recording()  # default encoding is `mp3`
    # recording_status.restart() --> trouver ou ça s'importe/tester sans

    await ctx.send("Started recording!", ephemeral=True)


@component_callback("stop_recording")
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


@slash_command("record")
async def record(ctx):
    await ctx.send(
        "Click the button to start recording!",
        components=[
            Button(
                custom_id="start_recording", label="Start Recording", style=ButtonStyle.PRIMARY
            ),
            Button(
                custom_id="stop_recording", label="Stop Recording", style=ButtonStyle.DANGER
            ),
        ],
    )
