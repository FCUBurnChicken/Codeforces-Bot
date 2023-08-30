import time
import discord

from discord.ext import commands
from utils import cf_api
from utils import view
from data import connect

class Duel(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cf = cf_api.Codeforces_API()
        self.db = connect.Connect()

    # 對戰指令duel
    @commands.hybrid_command(name="duel", description="透過 tag 使用者名稱來進行對戰")
    async def duel(self, ctx: commands.Context):
        if self.db.get_handle_info(ctx.guild.id, ctx.author.id) == None:
            await ctx.send(content = f"很抱歉，你還未與機器人註冊 codeforces 帳號")
            return
        msg_ctx = await ctx.send(content="**請 tag 你的對手**", view=None, ephemeral=True)
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        who = await self.client.wait_for("message", check=check)
        await who.delete()

        Player1_handle = self.db.get_handle_info(ctx.guild.id, ctx.author.id)[2]
        while who.mentions[0].id == ctx.author.id:
            await msg_ctx.edit(content = f"很抱歉，你不能 tag 你自己\n" +
                                         f"**請 tag 其他對手**")
            who = await self.client.wait_for("message", check=check)
            await who.delete()
        while self.db.get_handle_info(ctx.guild.id, who.mentions[0].id) == None:
            await msg_ctx.edit(content = f"很抱歉，你 tag 的對手還未與機器人註冊該 codeforces 帳號\n" +
                                         f"**請 tag 其他對手**")
            who = await self.client.wait_for("message", check=check)
            await who.delete()
        Player2_handle = self.db.get_handle_info(ctx.guild.id, who.mentions[0].id)[2]

        # 詢問題目難度範圍(僅需詢問發起對戰的人)
        await msg_ctx.edit( content = f"**請輸入題目難度範圍(最低/最高)**"
                            )
        msg = await self.client.wait_for("message", check=check)
        await msg.delete()
        while int(msg.content.split("/")[0]) > int(msg.content.split("/")[1]):
            await msg_ctx.edit( content = f"錯誤：最低範圍不能高於最高範圍\n" + 
                                          f"**請重新輸入題目難度範圍(最低/最高)**"
                                )
            msg = await self.client.wait_for("message", check=check)
            await msg.delete()
        min_rating = int(msg.content.split("/")[0])
        max_rating = int(msg.content.split("/")[1])
        # 詢問題目數量(僅需詢問發起對戰的人)
        await msg_ctx.edit( content = f"目前的篩選條件：\n" +
                                      f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                      f"============================================\n" +
                                      f"**請輸入你需要的題目數量(最多五題)**", view = None)
        msg = await self.client.wait_for("message", check=check)
        await msg.delete()
        while int(msg.content) <= 0 or int(msg.content) > 5:
            await msg_ctx.edit( content = f"錯誤：無法處理你要求的題目數量\n" +
                                          f"============================================\n" + 
                                          f"目前的篩選條件：\n" +
                                          f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                          f"============================================\n" + 
                                          f"**請重新輸入你需要的題目數量(最多五題)**", view = None)
            msg = await self.client.wait_for("message", check=check)
            await msg.delete()
        num = int(msg.content)
        # 選出題目
        Player1_AC_problem = self.cf.get_AC_problem(Player1_handle)
        Player2_AC_problem = self.cf.get_AC_problem(Player2_handle)
        problems = self.db.find_problem_by_tags_and_rating([], min_rating, max_rating)
        # 去除已經AC的題目
        for i in problems:
            if i in Player1_AC_problem or i in Player2_AC_problem:
                problems.remove(i)
        # 題目數量不足
        if len(problems) < num:
            await msg_ctx.edit(content= f"目前的篩選條件：\n" +
                                        f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                        f"============================================\n" + 
                                        f"錯誤：無法找到符合條件的題目\n" +
                                        f"============================================\n" + 
                                        f"請重新設定題目難度範圍或是題目數量", view = None)
            return
        # 隨機選出題目
        random_problem = []
        for i in range(num):
            random_problem.append(problems.pop(int(time.time()) % len(problems)))
        # 表格化輸出題目
        embed = discord.Embed(title="Problems", color=0x00ff00)
        embed.add_field(name="Problem Name", value="\n".join([f"[{i[2]}](https://codeforces.com/problemset/problem/{i[0]}/{i[1]})" for i in random_problem]), inline=True)
        embed.add_field(name="Rating", value="\n".join([f"{i[3]}" for i in random_problem]), inline=True)
        await msg_ctx.edit( content = f"以下是為 {ctx.author} 與 {who.mentions[0].name} 所篩選出來的 {num} 道題目\n" +
                                      f"- 難度介於 {min_rating} ~ {max_rating}\n",
                            embed = embed, 
                            view = None)

async def setup(client: commands.Bot):
    await client.add_cog(Duel(client))