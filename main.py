import settings
import discord
from discord.ext import commands
from discord import app_commands
from utils import cf_api
import json

cf = cf_api.Codeforces_API()
logger = settings.logging.getLogger('client')

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
        
        # 下載 cogs 的程式
        for cogs_file in settings.COGS_DIR.glob("*.py"):
            if cogs_file != "__init__.py":
                await client.load_extension(f"cogs.{cogs_file.name[:-3]}")
        
        # 斜線指令同步
        client.tree.copy_global_to(guild=settings.GUILD_ID)
        await client.tree.sync(guild=settings.GUILD_ID)

        # 準備好就在頻道打印 Bot ready
        logging_channel = await client.fetch_channel(settings.LOGGING_CHANNEL)
        await logging_channel.send(f"Bot ready")

        # 抓取 problem_list
        problem_list = await cf.get_problem_list()
        with open('problem_list.json', 'w') as f:
            json.dump(problem_list, f)


    @client.command()
    async def reload(ctx, cogs):
        await client.reload_extension(f"cogs.{cogs}")        

    client.run(settings.BOT_TOKEN, root_logger=True)

if __name__ == '__main__':
    main()