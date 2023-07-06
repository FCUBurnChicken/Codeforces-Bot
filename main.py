import settings
import discord
import requests
import json
from discord.ext import commands
from discord import app_commands

logger = settings.logging.getLogger('client')
url = "https://codeforces.com/api"

def get_user_info(handle):
    response = requests.get(url + "/user.info?handles=" + handle)
    response = json.loads(response.text)
    return {
        'handle': handle,
        'rating': response['result'][0]['rating'],
        'maxRating': response['result'][0]['maxRating'],
        'rank': response['result'][0]['rank'],
        'maxRank': response['result'][0]['maxRank']
    }

def main():
    intents = discord.Intents.all()
    client = commands.Bot(
        command_prefix="$",
        intents=intents
    )

    @client.event
    async def on_ready():
        # 將 info 訊息打印在 logs
        logger.info(f'User: {client.user} (ID: {client.user.id})')

        for cmd_file in settings.CMDS_DIR.glob("*.py"):
            if cmd_file != "__init__.py":
                await client.load_extension(f"cmds.{cmd_file.name[:-3]}")
        
        for cogs_file in settings.COGS_DIR.glob("*.py"):
            if cogs_file != "__init__.py":
                await client.load_extension(f"cogs.{cogs_file.name[:-3]}")
        
        # await client.load_extension("slashcmds.math_")

        client.tree.copy_global_to(guild=settings.GUILD_ID)
        await client.tree.sync(guild=settings.GUILD_ID)

    @client.command()
    async def reload(ctx, cogs):
        await client.reload_extension(f"cogs.{cogs}")

    @client.command()
    async def user(ctx, handle):
        response = get_user_info(handle)
        user_info = f"Handle: {response['handle']}\nRating: {response['rating']}\nMax Rating: {response['maxRating']}\nRank: {response['rank']}\nMax Rank: {response['maxRank']}"
        await ctx.send(user_info)
    
    client.run(settings.BOT_TOKEN, root_logger=True)

if __name__ == '__main__':
    main()