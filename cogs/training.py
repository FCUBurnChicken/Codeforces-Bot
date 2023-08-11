import time
import discord

from discord.ext import commands
from utils import cf_api
from utils import view
from data import connect

class Training(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cf = cf_api.Codeforces_API()
        self.db = connect.Connect()
    
    # 訓練指令training
    @commands.hybrid_command(name="training", description="透過詢問使用者的題目難度和題目類型來找出題目")
    async def training(self, ctx: commands.Context):
        msg_ctx = await ctx.send(content="**請輸入題目難度範圍(最低/最高)**", view=None, ephemeral=True)
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
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
        _view = view.MyViews()
        await msg_ctx.edit( content = f"目前的篩選條件：\n" +
                                      f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                      f"============================================\n" +
                                      f"**請選擇題目類型**\n" +
                                      f"註：因為總共有 36 個 tags 但是 discord 的單個列表只能接受 25 個選項，因此才會有兩個列表\n" +
                                      f"註：每個列表都可以複選",
                            view = _view)
        await _view.wait()
        tags = _view.tags_select
        await msg_ctx.edit(content = f"目前的篩選條件：\n" +
                                     f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                     f"- 題目類型需包含 {'、'.join(map(str, tags))}\n" +
                                     f"============================================\n" + 
                                     f"**請輸入你需要的題目數量(最多五題)**", view = None)
        msg = await self.client.wait_for("message", check=check)
        await msg.delete()
        while int(msg.content) <= 0 or int(msg.content) > 5:
            await msg_ctx.edit( content = f"錯誤：無法處理你要求的題目數量\n" +
                                          f"============================================\n" + 
                                          f"目前的篩選條件：\n" +
                                          f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                          f"- 題目類型需包含 {'、'.join(map(str, tags))}\n" +
                                          f"============================================\n" + 
                                          f"**請重新輸入你需要的題目數量(最多五題)**", view = None)
            msg = await self.client.wait_for("message", check=check)
            await msg.delete()
        num = int(msg.content)
        handle = self.db.get_handle_info(ctx.guild.id, ctx.author.id)[2]
        await msg_ctx.edit(content= f"目前的篩選條件：\n" +
                                    f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                    f"- 題目類型需包含 {'、'.join(map(str, tags))}\n" +
                                    f"============================================\n" + 
                                    f"正在查詢題目，請稍後", view = None)
        problems = self.db.find_problem_by_tags_and_rating(tags, min_rating, max_rating)
        AC_problem = self.cf.get_AC_problem(handle)
        # 去除已經AC的題目
        for i in problems:
            if i in AC_problem:
                problems.remove(i)
        # 題目數量不足
        if len(problems) == 0:
            await msg_ctx.edit(content=f"很抱歉，沒有符合該條件的題目，請重新輸入")
            return
        if len(problems) < num:
            _view = view.YesNoViews()
            await msg_ctx.edit(content=f"此篩選條件的題目數量為 {len(problems)}，少於你要求的數量，請問是否繼續", view=_view)
            await _view.wait()
            if _view.result:
                num = len(problems)
            else: 
                return
        
        # 隨機選出題目
        random_problem = []
        for i in range(num):
            # 不能有重複題目
            random_problem.append(problems.pop(int(time.time()) % len(problems)))
        # 表格化輸出題目(橫軸第一欄為題目名稱第二欄為難度)
        embed = discord.Embed(title="Problems", color=0x00ff00)
        embed.add_field(name="Problem Name", value="\n".join([f"[{i[2]}](https://codeforces.com/problemset/problem/{i[0]}/{i[1]})" for i in random_problem]), inline=True)
        embed.add_field(name="Rating", value="\n".join([f"{i[3]}" for i in random_problem]), inline=True)
        await msg_ctx.edit( content = f"以下是為你所篩選出來的 {num} 道題目\n" +
                                      f"- 難度介於 {min_rating} ~ {max_rating}\n" +
                                      f"- 題目類型需包含 `{'`、`'.join(map(str, tags))}`",
                            embed = embed, 
                            view = None)

        
async def setup(client: commands.Bot):
    await client.add_cog(Training(client))