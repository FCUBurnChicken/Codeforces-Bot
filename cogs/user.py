import time
import discord
from discord.ext import commands
from utils import cf_api
from utils import pagination
from data import connect

class User(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.cf = cf_api.Codeforces_API()
        self.db = connect.Connect()
    
    @commands.hybrid_group(name="handle")
    async def handle(self, ctx: commands.Context):
        await ctx.send("This is handle command")

    @handle.command(name="user", description="顯示該名用戶的 codeforces 資訊")
    async def user(self, ctx: commands.Context, member: discord.Member = None):
        member = ctx.author if member is None else member
        # 確認是否有註冊
        data = self.db.get_handle_info(ctx.guild.id, member.id)
        if data is None:
            await ctx.send("There isn't this user in database. Please find another!")
            ctx.command.reset_cooldown(ctx)
            return

        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.set_author(name=f"User {member.display_name}'s Handle", icon_url=member.display_avatar)
        embed.set_footer(text="This is Footer")
        embed.add_field(name="Handle", value=f"{data[2]}", inline=False)
        embed.add_field(name="Rating", value=f"{data[3]}", inline=False)
        embed.add_field(name="Rank", value=f"{data[4]}", inline=False)
        embed.set_thumbnail(url=f"{data[5]}")
        await ctx.send(embed = embed, ephemeral=True)

    @handle.command(name="identify", description="向機器人註冊 codeforces 帳號")
    async def identify(self, ctx: commands.Context, name: str):
        # 確認是否已經註冊
        data = self.db.get_handle_info(ctx.guild.id, ctx.author.id)
        if data:
            await ctx.send(f"Your handle is already set to {data}, ask an admin or mod to remove it first and try again.")
            ctx.command.reset_cooldown(ctx)
            return
        
        data = self.cf.get_user_info(name)
        rating, rank = (0, "unrated") if  "rating" not in data else (data['rating'], data['rank'])
        handle, photo =  data['handle'], data['titlePhoto']
        self.db.add_handle(ctx.guild.id, ctx.author.id, handle, rating, rank, photo)

        embed = discord.Embed(color=discord.Color.dark_green())
        embed.description = f"Handle for {ctx.author.mention} successfully set to [{handle}](https://codeforces.com/profile/{handle})"
        embed.add_field(name="Rank", value=f"{rank}", inline=True)
        embed.add_field(name='Rating', value=f'{rating}', inline=True)
        embed.set_thumbnail(url=f"{photo}")
        await ctx.send(embed=embed, ephemeral=True)

    @handle.command(name="set", description="更新自己的 codeforces 帳號設定")
    async def set(self, ctx: commands.Context, name: str):
        data = self.cf.get_user_info(name)
        rating, rank = (0, "unrated") if  "rating" not in data else (data['rating'], data['rank'])
        handle, photo =  data['handle'], data['titlePhoto']
        self.db.change_handle(handle, rating, rank, photo, ctx.guild.id, ctx.author.id)

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
            try:
                user = await self.client.fetch_user(int(handle[1]))
            except:
                print(f"{handle[2]} 不存在")
                continue
            data.append([{
                "label": "name",
                "item": user.display_name,
            },{
                "label": "handle",
                "item": handle[2],
            },{
                "label": "rating",
                "item": str(handle[3]),
            }])
        pagination_view = pagination.PaginationView(timeout=None)
        pagination_view.data = data
        await pagination_view.send(ctx)
        
async def setup(client: commands.Bot):
    await client.add_cog(User(client))