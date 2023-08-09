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

    # 訓練指令training
    @commands.command(name="training", description="透過詢問使用者的題目難度和題目類型來找出題目")
    async def training(self, ctx: commands.Context):
        await ctx.send("請輸入題目難度範圍(最低/最高)")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        msg = await self.client.wait_for("message", check=check)
        min_rating = int(msg.content.split("/")[0])
        max_rating = int(msg.content.split("/")[1])
        await ctx.send("請輸入題目類型(以,分隔)")
        msg = await self.client.wait_for("message", check=check)
        tags = msg.content.split(",")
        await ctx.send("請輸入你需要的題目數量(最多五題)")
        msg = await self.client.wait_for("message", check=check)
        num = int(msg.content)
        handle = self.db.get_handle_info(ctx.guild.id, ctx.author.id)[2]
        await ctx.send("正在查詢題目，請稍後")
        problems = self.cf.find_problem_by_tags_and_rating(tags, min_rating, max_rating)
        AC_problem = self.cf.get_AC_problem(handle)
        # 去除已經AC的題目
        for i in problems:
            if i in AC_problem:
                problems.remove(i)
        # 題目數量不足
        if len(problems) < num:
            await ctx.send("題目數量不足，請重新輸入")
            return
        # 隨機選出題目
        random_problem = []
        for i in range(num):
            # 不能有重複題目
            random_problem.append(problems.pop(int(time.time()) % len(problems)))
        # 表格化輸出題目(橫軸第一欄為題目名稱第二欄為難度)
        embed = discord.Embed(title="Problems", color=0x00ff00)
        embed.add_field(name="Problem Name", value="\n".join(["[" + i['name'] + "]" + "(https://codeforces.com/problemset/problem/" + str(i['id']) + "/" + i['index'] + ")" for i in random_problem]), inline=True)
        embed.add_field(name="Rating", value="\n".join([str(i['rating']) for i in random_problem]), inline=True)
        await ctx.send(embed = embed)

        
async def setup(client: commands.Bot):
    await client.add_cog(User(client))