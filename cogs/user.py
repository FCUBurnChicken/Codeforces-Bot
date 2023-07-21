import discord
from discord.ext import commands
import typing
from utils import cf_api
from data import connect

class User(commands.Cog):
    def __init__(self, client) -> None:
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
        all_data = self.db.get_all_handle()
        discord_id, handle, rating, rank, discord_name = [], [], [], [], []
        for data in all_data:
            discord_id.append(data[1])
            handle.append(data[2])
            rating.append(str(data[3]))
            rank.append(data[4])
        for id in discord_id:
            user = await self.client.fetch_user(int(id))
            discord_name.append(user.display_name)
        embed = discord.Embed(title="所有已註冊的 codeforces 名單", color=discord.Color.dark_green())
        embed.add_field(name="Handle", value="\n".join(handle), inline=True)
        # embed.add_field(name="Discord User", value="\n".join(discord_name), inline=True)
        embed.add_field(name='Rating', value="\n".join(rating), inline=True)
        embed.add_field(name="Rank", value="\n".join(rank), inline=True)        
        await ctx.send(embed=embed, ephemeral=True)
        
async def setup(client: commands.Bot):
    await client.add_cog(User(client))