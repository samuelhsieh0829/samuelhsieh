import discord
from discord.ext import commands
from discord import app_commands
import dotenv
import os
import GPT
import time

dotenv.load_dotenv()

dctoken = os.getenv("DCTOKEN")
owner_id = int(os.getenv("OWNERID"))
cooldown = int(os.getenv("COOLDOWN"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
gpt = GPT.GPT()

used_time = time.time()

def check_user(user_id:int):
    if user_id == owner_id:
        return True
    else:
        return False

@client.event
async def on_ready():
    print("Logging as {}".format(client.user))
    try:
        await client.tree.sync()
        owner = await client.fetch_user(owner_id)
        game = discord.Game("Cosplay {}".format(owner.name))
        await client.change_presence(activity=game)
    except Exception as e:
        print(e)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    global used_time
    if time.time() - used_time < cooldown:
        print(time.time() - used_time)
        return
    if not ((f"<@{client.user.id}>" in message.content) or (f"<@{owner_id}>" in message.content)):
        return
    async with message.channel.typing():
        global gpt
        print(message.content)
        response = gpt.message_request(message.content, user=message.author.name)
        used_time = time.time()
        await message.channel.send(response)
    
@client.tree.command(name="load_prompt", description="Reload base Prompt")
async def load_prompt(ctx: discord.Interaction):
    if check_user:
        global gpt
        gpt.load_prompt()
        print("Prompt reloaded")
        await ctx.response.send_message("Reloaded prompt")
    else:
        print(f"{ctx.user.name} tried to reload prompt")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="history", description="View chat history")
async def history(ctx: discord.Interaction):
    if check_user:
        print(gpt.chat_history)
        await ctx.response.send_message(gpt.chat_history)
    else:
        print(f"{ctx.user.name} tried to see chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="clear_history", description="Clear chat history")
async def clear_history(ctx: discord.Interaction):
    if check_user:
        gpt.clear_history()
        await ctx.response.send_message("Done")
    else:
        print(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

@client.tree.command(name="change_prompt", description="Change base prompt")
async def change_prompt(ctx: discord.Interaction, filename:str):
    if check_user:
        gpt.clear_history()
        gpt.change_base_prompt(filename)
        await ctx.response.send_message("Done")
    else:
        print(f"{ctx.user.name} tried to clear chat history")
        await ctx.response.send_message(f"<@{ctx.user.id}>是傻逼")

client.run(token=dctoken)