import discord
from discord.ext import commands
from google import genai
import urllib.request
import requests
from google.genai import types
import json

with open('./config.json', 'r') as file:
    config = json.load(file)

channel_id = int(config["channel_id"])

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "$", case_insensitive=True, intents=intents)

client = genai.Client(api_key=config["ai_api_key"])

dict_chat_started = {}


@bot.event
async def on_ready():
    print(f"login bot --> {bot.user}")


@bot.command(name = "start", description = "start")
async def start(ctx, *args):
    if (ctx.channel.id != channel_id):
        print("incorrect channel")
        await ctx.message.reply(f"{ctx.author.mention} you can only use this command in the {bot.get_channel(channel_id)} channel")
    elif (ctx.author.id in dict_chat_started):
        print("already started")
        await ctx.message.reply(f"{ctx.author.mention} you have already started a conversation. use $terminate to terminate the chat or $restart to start a new conversation")
    else:
        print("start")
        dict_chat_started[ctx.author.id] = client.chats.create(model="gemini-2.0-flash")
        await ctx.message.reply(f"{ctx.author.mention} your convertsation start. say something. use $terminate to terminate the chat or $restart to start a new conversation")
        
        
@bot.command(name = "terminate", description = "terminate")
async def terminate(ctx, *args):
    if (ctx.channel.id != channel_id):
        await ctx.message.reply(f"{ctx.author.mention} you can only use this command in the chat-bot-test channel")
    elif (ctx.author.id not in dict_chat_started):
        await ctx.message.reply(f"{ctx.author.mention} you haven't started a conversation. use $start to start the chat")
    else:
        del dict_chat_started[ctx.author.id]
        await ctx.message.reply(f"{ctx.author.mention} your convertsation terminated. use $start to start a new conversation")
        
@bot.command(name = "restart", description = "restart")
async def terminate(ctx, *args):
    if (ctx.channel.id != channel_id):
        await ctx.message.reply(f"{ctx.author.mention} you can only use this command in the chat-bot-test channel")
    elif (ctx.author.id not in dict_chat_started):
        await ctx.message.reply(f"{ctx.author.mention} you haven't started a conversation. use $start to start the chat")
    else:
        dict_chat_started[ctx.author.id] = client.chats.create(model="gemini-2.0-flash")
        await ctx.message.reply(f"{ctx.author.mention} your convertsation restart. say something. use $terminate to terminate the chat or $restart to start a new conversation")
        
  
@bot.event
async def on_message(message):
    # if message.author != bot.user: 
    #     print(f"message.attchments:{message.attachments}")
    # return
    if message.author == bot.user or (not message.content.startswith("$") and message.author.id not in dict_chat_started) or not message.content:
        return
    if message.content.startswith("$"):
        await bot.process_commands(message)
        return
    if len(message.content) > 500:
        message.delete()
        await message.reply(f"{message.author.mention} your message is too long. Please keep it under 500 characters")

    if message.channel.id != channel_id:
        await message.channel.reply(f"{message.author.mention} you can only use this command in the chat-bot-test channel")
    else:
        if message.author.id in dict_chat_started:
            if message.attachments:
                contents = [message.content]
                for attachment in message.attachments:
                    image = requests.get(attachment.url)
                    contents.append(types.Part.from_bytes(data=image.content, mime_type=attachment.content_type))
                response = dict_chat_started[message.author.id].send_message(contents)
                await message.reply(response.text)
            else:
                response = dict_chat_started[message.author.id].send_message(message.content)
                await message.reply(response.text)
        else:
            await message.reply(f"{message.author.mention} you haven't started a conversation. use $start to start the chat")
    await bot.process_commands(message) 

bot.run(config["discord_token"])
