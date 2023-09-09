import time
import discord
from discord import app_commands
from discord.ext import commands
from utils import cf_api
from utils import pagination
from data import connect

class Handle(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.cf = cf_api.Codeforces_API()
        self.db = connect.Connect()
    
    @commands.hybrid_group(name="handle")
    async def handle(self, ctx: commands.Context):
        await ctx.send("This is handle command")

    @handle.command(name="user", description="顯示該名用戶的 codeforces 資訊")
    @app_commands.describe(member="要查詢的成員。如果要查詢自己，可以省略此參數")
    async def user(self, ctx: commands.Context, member: discord.Member = None):
        member = ctx.author if member is None else member
        # 確認是否有註冊
        data = self.db.get_handle_info(member.id, member.display_name)
        if data is None:
            await ctx.send(content="There isn't this user in database. Please find another!", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            return

        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.set_author(name=f"User {member.display_name}'s Handle", icon_url=member.display_avatar)
        embed.set_footer(text="This is Footer")
        embed.add_field(name="Handle", value=f"{data[2]}", inline=False)
        embed.add_field(name="Rating", value=f"{data[3]}", inline=False)
        embed.add_field(name="Rank", value=f"{data[4]}", inline=False)
        embed.set_thumbnail(url=f"{data[5]}")
        await ctx.send(embed=embed, ephemeral=True)

    @handle.command(name="identify", description="向機器人註冊 codeforces 帳號")
    @app_commands.describe(handle_name="你的 cf handle 名稱")
    async def identify(self, ctx: commands.Context, handle_name: str):
        # 確認是否已經註冊
        data = self.db.get_handle_info(ctx.author.id, ctx.author.display_name)
        if data:
            await ctx.send(content=f"Your handle is already set to {data[2]}, ask an admin or mod to remove it first and try again.", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            return
        
        data = await self.cf.get_user_info(handle_name)
        rating, rank = (0, "unrated") if  "rating" not in data else (data['rating'], data['rank'])
        handle, photo =  data['handle'], data['titlePhoto']
        self.db.add_handle(ctx.author.id, ctx.author.display_name, handle, rating, rank, photo)

        embed = discord.Embed(color=discord.Color.dark_green())
        embed.description = f"Handle for {ctx.author.mention} successfully set to [{handle}](https://codeforces.com/profile/{handle})"
        embed.add_field(name="Rank", value=f"{rank}", inline=True)
        embed.add_field(name='Rating', value=f'{rating}', inline=True)
        embed.set_thumbnail(url=f"{photo}")
        await ctx.send(embed=embed, ephemeral=True)

    @handle.command(name="set", description="更新自己的 codeforces 帳號設定")
    @app_commands.describe(handle_name="你的 cf handle 名稱")
    async def set(self, ctx: commands.Context, handle_name: str):
        data = await self.cf.get_user_info(handle_name)
        rating, rank = (0, "unrated") if  "rating" not in data else (data['rating'], data['rank'])
        handle, photo =  data['handle'], data['titlePhoto']
        self.db.change_handle(handle, rating, rank, photo, ctx.author.display_name, ctx.author.id)

        embed = discord.Embed(color=discord.Color.dark_green())
        embed.description = f"Handle for {ctx.author.mention} successfully set to [{handle}](https://codeforces.com/profile/{handle})"
        embed.add_field(name="Rank", value=f"{rank}", inline=True)
        embed.add_field(name='Rating', value=f'{rating}', inline=True)
        embed.set_thumbnail(url=f"{photo}")
        await ctx.send(embed=embed, ephemeral=True)
    
    @handle.command(name="list", description="列出已註冊名單")
    async def list(self, ctx: commands.Context):
        handles = self.db.get_all_handle()
        data = []
        for handle in handles:
            data.append([{
                "label": "name",
                "item": handle[1],
            },{
                "label": "handle",
                "item": handle[2],
            },{
                "label": "rating",
                "item": str(handle[3]),
            }])
        pagination_view = pagination.PaginationView(title="User List")
        pagination_view.data = data
        await pagination_view.send(ctx)
    
    @handle.command(name="solved", description="列出已解的題目")
    @app_commands.describe(member="要查詢的成員。如果要查詢自己，可以省略此參數")
    async def solved(self, ctx: commands.Context, member: discord.Member = None):
        member = ctx.author if member is None else member
        handle = self.db.get_handle_info(member.id, member.display_name)
        if handle is None:
            await ctx.send(content="There isn't this user in database. Please find another!", ephemeral=True)
            ctx.command.reset_cooldown(ctx)
            return

        handle = handle[2]
        AC_problems = await self.cf.get_AC_problem(handle)
        data = []
        for item in AC_problems:
            data.append([{
                "label": "name",
                "item": f"[{item[2]}](https://codeforces.com/problemset/problem/{item[0]}/{item[1]})",
            },{
                "label": "rating",
                "item": str(item[3]),
            }])
        pagination_view = pagination.PaginationView(sep=10, title=f"{handle} Solved Problems List")
        pagination_view.data = data
        await pagination_view.send(ctx)
        
async def setup(client: commands.Bot):
    await client.add_cog(Handle(client))