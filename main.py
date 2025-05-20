import discord
from discord.ext import commands, tasks
import dotenv
import os
import GPT
import time
import aioconsole
import logging
from typing import Optional
from collections import deque
# import pyaudio
import io
import threading

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('\x1b[36m{asctime} {levelname:<8} {name}: \x1b[37m{message}\x1b[0m', dt_fmt, style='{')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

dotenv.load_dotenv()

dctoken = os.getenv("DCTOKEN")
owner_id = int(os.getenv("OWNERID"))
cooldown_time = int(os.getenv("COOLDOWN"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
gpt = GPT.GPT()

used_time = time.time()
status = True
on__mention = True
cooldown = True
voice_record: dict[discord.VoiceClient, deque] = {}

local_audio = io.BytesIO()

def check_user(user_id:int):
    if user_id == owner_id:
        return True
    else:
        return False

channel = int(os.getenv("DEFAULT_CHANNEL"))
playing = ""

@tasks.loop()
async def command():
    global channel, playing
    cmd = await aioconsole.ainput()
    temp = cmd.split()
    l = list(temp[0])
    if l[0] == "/":
        if temp[0] == "/channel":
            if len(temp) != 1:
                channel = temp[1]
                channel_name = await client.fetch_channel(channel)
                log.info(f"Channel Changed to {channel}, {channel_name}")
            else:
                channel_name = await client.fetch_channel(channel)
                log.info(f"Channel = {channel}, {channel_name}")
        elif temp[0] == "/play":
            if len(temp) != 1:
                activity = discord.Game(name=temp[1])
                await client.change_presence(activity=activity)
                playing = temp[1]
                log.info(f"Play {temp[1]}")

            else:
                log.info(f"Playing {playing}")
        elif temp[0] == "/add":
            if len(temp) != 1:
                user = await client.fetch_user(int(temp[1]))
                log.info(f"Add {user.name}")
                channel = await user.create_dm()
                channel = channel.id
            else:
                log.warning("No input")
        # elif temp[0] == "/join":
        #     if len(temp) != 1:
        #         vc_channel = await client.fetch_channel(int(temp[1]))
        #         if vc_channel.type != discord.ChannelType.voice:
        #             log.warning("Not a voice channel")
        #             return
        #         log.info(f"Join {vc_channel.name}")
        #         vc_client = await vc_channel.connect()
        #         send_audio_thread = threading.Thread(target=send_audio, args=(vc_client,))
        #         send_audio_thread.start()
        #     else:
        #         log.warning("Please input channel id")
        # elif temp[0] == "/leave":
        #     if len(temp) != 1:
        #         vc_channel = await client.fetch_channel(int(temp[1]))

        #         if vc_channel.type != discord.ChannelType.voice:
        #             log.warning("Not a voice channel")
        #             return
                
        #         log.info(f"Leave {vc_channel.name}")
        #         voice_client = discord.utils.get(client.voice_clients, guild=vc_channel.guild)
        #         if voice_client is None:
        #             log.warning("Not in a voice channel")
        #             return
                
        #         await voice_client.disconnect()

        #     else:
        #         log.warning("Please input channel id")
    else:
        try:
            channel_name = await client.fetch_channel(channel)
            log.info(f"Sending {cmd} to {channel}, {channel_name}")
            talk = await client.fetch_channel(channel)
            await talk.send(cmd)
        except:
            log.exception("Error while sending message:")

# @tasks.loop(seconds=1)
# async def record_audio():
#     for vc, buffer in voice_record.items():
#         if vc.is_connected():
#             vc.record(discord.sinks.RawDataSink(buffer))
#         else:
#             log.info("Not connected")

# @tasks.loop(seconds=1)
# async def process_voice_command():
#     for vc, buffer in voice_record.items():
#         audio_file = write_buffer_to_tempfile(buffer)
#         text = transcribe_audio(audio_file)
#         if detect_trigger(text):
#             response = gpt.generate_response(text)
#             speech_file = generate_tts(response)
#             vc.play(discord.FFmpegPCMAudio(speech_file))

# class MicrophoneAudio(discord.AudioSource):
#     def __init__(self):
#         self.p = pyaudio.PyAudio()
#         self.stream = self.p.open(
#             format=pyaudio.paInt16,
#             channels=2,
#             rate=48000,
#             input=True,
#             frames_per_buffer=960
#         )

#     def read(self):
#         return self.stream.read(960)

#     def is_opus(self):
#         return False  # We're sending raw PCM, not Opus

#     def cleanup(self):
#         self.stream.stop_stream()
#         self.stream.close()
#         self.p.terminate()

# def send_audio(vc: discord.VoiceClient):
#     audio_source = MicrophoneAudio()
#     vc.play(audio_source)

@client.event
async def on_ready():
    log.info("Logging as {}".format(client.user))
    try:
        global playing
        await client.tree.sync()
        owner = await client.fetch_user(owner_id)
        playing = "Cosplay {}".format(owner.name)
        game = discord.Game(playing)
        await client.change_presence(activity=game)
        command.start()
    except:
        log.exception("Error while starting:")

@client.event
async def on_message(message: discord.Message):
    if message.channel.type.name == "private":
        log.info(f"Message from {message.author.name} ({message.author.id})-> {message.content}")
    if not status:
        return
    if message.author == client.user:
        return
    global used_time
    if time.time() - used_time < cooldown_time:
        if cooldown:
            log.info(time.time() - used_time)
            return
    if not ((f"<@{client.user.id}>" in message.content) or (f"<@{owner_id}>" in message.content)):
        if on__mention:
            return
    async with message.channel.typing():
        global gpt
        log.info(message.content)
        response = gpt.message_request(message.content, user=message.author.name)
        if len(response.split("謝恩: ")) >= 2:
            response = str(response[1])

        if ":genshin:" in response:
            response = response.replace(":genshin:", "<:genshin:1206198964638974002>")

        if ":val:" in response:
            response = response.replace(":val:", "<:val:1157681820184350920>")

        used_time = time.time()
        await message.channel.send(response)
    
@client.tree.command(name="load_prompt", description="Reload base Prompt")
async def load_prompt(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global gpt
        gpt.load_prompt()
        log.info("Prompt reloaded")
        await ctx.response.send_message("Reloaded prompt")
    else:
        log.info(f"{ctx.user.name} tried to reload prompt")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="history", description="View chat history")
async def history(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        try:
            log.info(gpt.chat_history)
            await ctx.response.send_message("```" + gpt.chat_history + "\n" + len(gpt.chat_history) + "```")
        except:
            await ctx.response.send_message(len(gpt.chat_history))
    else:
        log.info(f"{ctx.user.name} tried to see chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="clear_history", description="Clear chat history")
async def clear_history(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        gpt.clear_history()
        await ctx.response.send_message("Done")
    else:
        log.info(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="change_prompt", description="Change base prompt")
async def change_prompt(ctx: discord.Interaction, filename:str):
    if check_user(ctx.user.id):
        gpt.clear_history()
        gpt.change_base_prompt(filename)
        await ctx.response.send_message("Done")
    else:
        log.info(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="switch", description="Switch")
async def switch(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global status
        if status:
            status = False
            await ctx.response.send_message("Disabled")
            playing = "Sleeping😴"
            game = discord.Game(playing)
            await client.change_presence(activity=game)
        else:
            status = True
            await ctx.response.send_message("Enabled")
            owner = await client.fetch_user(owner_id)
            playing = "Cosplay {}".format(owner.name)
            game = discord.Game(playing)
            await client.change_presence(activity=game)
    else:
        log.info(f"{ctx.user.name} tried to switch")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="on_mention", description="Trigger by mention or not")
async def onmention(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global on__mention
        if on__mention:
            on__mention = False
            await ctx.response.send_message("Disabled on mention")
        else:
            on__mention = True
            await ctx.response.send_message("Enabled on mention")
    else:
        log.info(f"{ctx.user.name} tried to switch on mention")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="cooldown", description="Switch cooldown")
async def cooldownn(ctx: discord.Interaction, time:Optional[int]):
    if check_user(ctx.user.id):
        global cooldown, cooldown_time
        if cooldown:
            if time is None:
                cooldown = False
                await ctx.response.send_message("Disabled cooldown")
                return
            else:
                cooldown_time = time
                await ctx.response.send_message(f"Cooldown set to {time}", ephemeral=True)
        else:
            cooldown = True
            if time is None:
                await ctx.response.send_message("Enabled cooldown")
                return
            else:
                cooldown_time = time
                await ctx.response.send_message(f"Cooldown enabled, set to {time}", ephemeral=True)
    else:
        log.info(f"{ctx.user.name} tried to switch cooldown")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

# @client.tree.command(name="join", description="Join a voice channel")
# async def join(ctx: discord.Interaction):
#     if check_user(ctx.user.id):
#         if ctx.user.voice is None:
#             await ctx.response.send_message("You are not in a voice channel")
#             return
#         channel = ctx.user.voice.channel
#         await channel.connect()
#         await ctx.response.send_message(f"Joined {channel}")
#     else:
#         log.info(f"{ctx.user.name} tried to use join")
#         await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

# @client.tree.command(name="leave", description="Leave a voice channel")
# async def leave(ctx: discord.Interaction):
#     if check_user(ctx.user.id):
#         if ctx.user.voice is None:
#             await ctx.response.send_message("You are not in a voice channel")
#             return
#         channel = ctx.user.voice.channel
#         voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
#         if voice_client is None:
#             await ctx.response.send_message("Not in a voice channel")
#             return
#         await voice_client.disconnect()
#         await ctx.response.send_message(f"Left {channel}")
#     else:
#         log.info(f"{ctx.user.name} tried to use leave")
#         await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.error
async def on_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        log.exception("Error in command:")
        await interaction.response.send_message(f"Unknown Error: {error}", ephemeral=True)

client.run(token=dctoken)