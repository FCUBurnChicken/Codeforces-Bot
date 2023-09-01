import settings
import discord
from discord.ext import commands
from utils import cf_api
from data import connect
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

cf = cf_api.Codeforces_API()
conn = connect.Connect()
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
        
        # 創建資料庫
        conn.build_handles()

    @client.event
    async def on_connect():
        logging_channel = await client.fetch_channel(settings.LOGGING_CHANNEL)
        await logging_channel.send(f"Bot ready")
    
    @client.event
    async def on_disconnect():
        logging_channel = await client.fetch_channel(settings.LOGGING_CHANNEL)
        await logging_channel.send(f"Bot left")

    @client.command()
    async def reload(ctx, cogs):
        await client.reload_extension(f"cogs.{cogs}") 
    
    client.run(settings.BOT_TOKEN, root_logger=True)

if __name__ == '__main__':
    main()