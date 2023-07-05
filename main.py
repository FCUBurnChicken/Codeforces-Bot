import settings
import discord
from discord.ext import commands
from discord import app_commands

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

    client.run(settings.BOT_TOKEN, root_logger=True)

if __name__ == '__main__':
    main()