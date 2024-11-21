import discord
from discord.ext import commands, tasks
import dotenv
import os
import GPT
import time
import aioconsole

dotenv.load_dotenv()

dctoken = os.getenv("DCTOKEN")
owner_id = int(os.getenv("OWNERID"))
cooldown = int(os.getenv("COOLDOWN"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
gpt = GPT.GPT()

used_time = time.time()
status = True
on__mention = True
cooldown = True

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
                print(f"Channel Changed to {channel}, {channel_name}")
            else:
                channel_name = await client.fetch_channel(channel)
                print(f"Channel = {channel}, {channel_name}")
        elif temp[0] == "/play":
            if len(temp) != 1:
                activity = discord.Game(name=temp[1])
                await client.change_presence(activity=activity)
                playing = temp[1]
                print(f"Play {temp[1]}")

            else:
                print(f"Playing {playing}")
        elif temp[0] == "/add":
            if len(temp) != 1:
                user = await client.fetch_user(int(temp[1]))
                print(f"Add {user.name}")
                channel = await user.create_dm()
                channel = channel.id
            else:
                print("No input")
    else:
        try:
            channel_name = await client.fetch_channel(channel)
            print(f"Sending {cmd} to {channel}, {channel_name}")
            talk = await client.fetch_channel(channel)
            await talk.send(cmd)
        except Exception as e:
            print(e)

@client.event
async def on_ready():
    print("Logging as {}".format(client.user))
    try:
        global playing
        await client.tree.sync()
        owner = await client.fetch_user(owner_id)
        playing = "Cosplay {}".format(owner.name)
        game = discord.Game(playing)
        await client.change_presence(activity=game)
        command.start()
    except Exception as e:
        print(e)

@client.event
async def on_message(message: discord.Message):
    if message.channel.type.name == "private":
        print(f"Message from {message.author.name} ({message.author.id})-> {message.content}")
    if not status:
        return
    if message.author == client.user:
        return
    global used_time
    if time.time() - used_time < cooldown:
        if cooldown:
            print(time.time() - used_time)
            return
    if not ((f"<@{client.user.id}>" in message.content) or (f"<@{owner_id}>" in message.content)):
        if on__mention:
            return
    async with message.channel.typing():
        global gpt
        print(message.content)
        response = gpt.message_request(message.content, user=message.author.name)
        if len(response.split("謝恩: ")) >= 2:
            response = str(response[1])
        used_time = time.time()
        await message.channel.send(response)
    
@client.tree.command(name="load_prompt", description="Reload base Prompt")
async def load_prompt(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global gpt
        gpt.load_prompt()
        print("Prompt reloaded")
        await ctx.response.send_message("Reloaded prompt")
    else:
        print(f"{ctx.user.name} tried to reload prompt")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="history", description="View chat history")
async def history(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        try:
            print(gpt.chat_history)
            await ctx.response.send_message("```" + gpt.chat_history + "\n" + len(gpt.chat_history) + "```")
        except:
            await ctx.response.send_message(len(gpt.chat_history))
    else:
        print(f"{ctx.user.name} tried to see chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="clear_history", description="Clear chat history")
async def clear_history(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        gpt.clear_history()
        await ctx.response.send_message("Done")
    else:
        print(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="change_prompt", description="Change base prompt")
async def change_prompt(ctx: discord.Interaction, filename:str):
    if check_user(ctx.user.id):
        gpt.clear_history()
        gpt.change_base_prompt(filename)
        await ctx.response.send_message("Done")
    else:
        print(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="switch", description="Switch")
async def switch(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global status
        if status:
            status = False
            await ctx.response.send_message("Disabled")
        else:
            status = True
            await ctx.response.send_message("Enabled")
    else:
        print(f"{ctx.user.name} tried to switch")
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
        print(f"{ctx.user.name} tried to switch on mention")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="cooldown", description="Switch cooldown")
async def cooldownn(ctx: discord.Interaction):
    if check_user(ctx.user.id):
        global cooldown
        if cooldown:
            cooldown = False
            await ctx.response.send_message("Disabled cooldown")
        else:
            cooldown = True
            await ctx.response.send_message("Enabled cooldown")
    else:
        print(f"{ctx.user.name} tried to switch cooldown")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

client.run(token=dctoken)