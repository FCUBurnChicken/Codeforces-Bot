import discord
import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
from discord.ext import commands
from utils import cf_interaction
from utils import cf_api
from utils import view
from data import connect

class Round(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cf = cf_api.Codeforces_API()
        self.db = connect.Connect()

    @commands.hybrid_command(name="round", description="結合 codeforces content 的線上團練")
    async def round(self, ctx: commands.Context):
        _round = {
            "email": "",
            "password": "",
            "name": "",
            "startDay": "",
            "startTime": "",
            "players": []
        }
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        msg_ctx = await ctx.send(content="**請輸入團練賽的名稱**", view=None, ephemeral=True)
        msg = await self.client.wait_for("message", check=check)
        _round["name"] = msg.content
        await msg.delete()
        await msg_ctx.edit(content="**請輸入團練賽的開始日期**\n格式：YYYY/MM/DD\n範例：2023/08/29")
        msg = await self.client.wait_for("message", check=check)
        _round["startDay"]= msg.content
        await msg.delete()
        await msg_ctx.edit(content="**請輸入團練賽的開始時間**\n格式：HH:MM\n範例：12:00")
        msg = await self.client.wait_for("message", check=check)
        _round["startTime"]= msg.content
        await msg.delete()
        await msg_ctx.edit(content="**請輸入舉辦人的 codeforces 帳號**")
        msg = await self.client.wait_for("message", check=check)
        _round["email"]= msg.content
        await msg.delete()
        await msg_ctx.edit(content="**請輸入舉辦人的 codeforces 密碼**")
        msg = await self.client.wait_for("message", check=check)
        _round["password"]= msg.content
        await msg.delete()
        userSelect = view.UserView(client=self.client)
        await msg_ctx.edit(content="**請選擇參賽人員**", view=userSelect)
        await userSelect.wait()
        _round['players'] = userSelect.selectUser
        await msg_ctx.edit(content="**請輸入題目難度範圍(最低/最高)**", view=None)
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
        _view = view.TagSelect()
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
                                     f"- 題目類型為： `{'`、`'.join(map(str, tags))}`\n" +
                                     f"============================================\n" + 
                                     f"**請輸入你需要的題目數量(最多五題)**", view = None)
        msg = await self.client.wait_for("message", check=check)
        await msg.delete()
        while int(msg.content) <= 0 or int(msg.content) > 5:
            await msg_ctx.edit( content = f"錯誤：無法處理你要求的題目數量\n" +
                                          f"============================================\n" + 
                                          f"目前的篩選條件：\n" +
                                          f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                          f"- 題目類型為： `{'`、`'.join(map(str, tags))}`\n" +
                                          f"============================================\n" + 
                                          f"**請重新輸入你需要的題目數量(最多五題)**", view = None)
            msg = await self.client.wait_for("message", check=check)
            await msg.delete()
        num = int(msg.content)
        await msg_ctx.edit(content= f"目前的篩選條件：\n" +
                                    f"- 題目難度範圍: {min_rating} ~ {max_rating}\n" +
                                    f"- 題目類型為： `{'`、`'.join(map(str, tags))}`\n" +
                                    f"============================================\n" + 
                                    f"正在準備中，請稍後", view = None)
        
        problems = self.db.find_problem_by_tags_and_rating(tags, min_rating, max_rating)
        for player in _round['players']:
            print(player.display_name, player.id)
            handle = self.db.get_handle_info(player.id, player.display_name)[2]
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
            _view = view.ConfirmViews()
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
        
        round = cf_interaction.build_round(_round=_round)
        status_msg = await ctx.send(content=f"正在登錄中...", view=None, ephemeral=True)
        isLogin = round.login()
        while not isLogin:
            isLogin = round.login()
        await status_msg.edit(content=f"登錄成功")
        round.write_round_info()
        count = 0
        await status_msg.edit(content=f"正在加載題目...")
        for problem in random_problem:
            count += 1
            round.add_problems(problem)
            await status_msg.edit(content=f"第 {count} 道題目加載完成")
        round.create()
        await status_msg.edit(content=f"正在設定時間...")
        round.setupTime()
        round.add_to_group()
        await status_msg.edit(content=f"正在將 Contest 加入 Group...")
        time.sleep(5)
        round.close()
        await status_msg.delete()
        await msg_ctx.edit(content= f"團練賽已成功建立，請前往 codeforces 查看")

async def setup(client: commands.Bot):
    await client.add_cog(Round(client))