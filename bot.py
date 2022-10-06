# Imports
import discord
from discord.ext import commands
import os
import json
import tweepy
from tweepy import HTTPException

# Discord Intents
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(intents=intents, command_prefix='.')

# Getting config datas
conf = open("./config/config.json")
config = json.load(conf)

# Twitter auth
auth = tweepy.OAuth1UserHandler(os.environ["CONSUMER_KEY"],
                                os.environ["CONSUMER_SECRET"],
                                os.environ["ACCESS_TOKEN"],
                                os.environ["ACCESS_TOKEN_SECRET"])

api = tweepy.API(auth, wait_on_rate_limit=True)


# Discord Commands
@client.command()
async def add(ctx, username):
    try:
        user = api.get_user(screen_name=username)
        dicts = json.load(open('./config/config.json'))
        dicts['victims'].append(username)
        json_obj = json.dumps(dicts, indent=4)
        with open('./config/config.json', 'w') as f:
            f.write(json_obj)
        await ctx.send(f"{username} has been added successfully")
    except HTTPException as e:
        await ctx.send("User not found")


@client.command()
async def remove(ctx, username):
    dicts = json.load(open('./config/config.json'))
    if username in dicts['victims']:
        dicts['victims'].remove(username)
        json_obj = json.dumps(dicts, indent=4)
        with open('./config/config.json', 'w') as f:
            f.write(json_obj)
        await ctx.send(f"{username} has been removed successfully")
    else:
        await ctx.send(f"{username} was never added")

client.run(os.environ["DISCORD_TOKEN"])