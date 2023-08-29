import discord
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from discord.ext import commands
from utils import cf_api
from utils import view
from data import connect

month = {
    "01":"Jan",
    "02":"Feb",
    "03":"Mar",
    "04":"Apr",
    "05":"May",
    "06":"Jun",
    "07":"Jul",
    "08":"Aug",
    "09":"Sep",
    "10":"Oct",
    "11":"Nov",
    "12":"Dec"
}

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
            "startTime": ""
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
        await msg_ctx.edit(content="**請輸入題目難度範圍(最低/最高)**")
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
                                    f"正在準備中，請稍後", view = None)
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
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get("https://codeforces.com")
        element = browser.find_element(By.XPATH, "//a[@href='/enter?back=%2F']")
        element.click()
        time.sleep(2)
        element = browser.find_element(By.XPATH, "//input[@name='handleOrEmail']")
        element.send_keys(_round["email"])
        element = browser.find_element(By.XPATH, "//input[@name='password']")
        element.send_keys(_round["password"])
        element = browser.find_element(By.XPATH, "//input[@value='Login']")
        element.click()
        time.sleep(2)

        print("Login Success")
        browser.get("https://codeforces.com/mashup/new")
        time.sleep(2)
        element = browser.find_element(By.XPATH, "//input[@name='contestName']")
        element.send_keys(_round["name"])
        element = browser.find_element(By.XPATH, "//input[@name='contestDuration']")
        element.send_keys("180")
        problem_msg = await ctx.send(content=f"正在加載 {num} 道題目", view=None, ephemeral=True)
        count = 0
        for problem in random_problem:
            count += 1
            element = browser.find_element(By.XPATH, "//input[@name='problemQuery']")
            element.send_keys(f"{problem[0]}-{problem[1]}")
            element = browser.find_element(By.XPATH, "//img[@alt='Add problem']")
            element.click()
            await problem_msg.edit(content=f"第 {count} 道題目加載完成")
            time.sleep(5)
        element = browser.find_element(By.XPATH, "//input[@value='Create Mashup Contest']")
        element.click()
        time.sleep(2)
        contestId = browser.current_url.split("/")
        browser.get(f"https://codeforces.com/gym/edit/{contestId[-1]}")
        time.sleep(2)
        element = browser.find_element(By.XPATH, "//input[@name='startDay']")
        day = _round["startDay"].split("/")
        element.send_keys(f"{month[day[1]]}/{day[2]}/{day[0]}")
        element = browser.find_element(By.XPATH, "//input[@name='startTime']")
        element.send_keys(_round["startTime"])
        element = browser.find_element(By.XPATH, "//input[@value='Save changes']")
        element.click()
        time.sleep(2)
        browser.get("https://codeforces.com/group/GFWL4cNHNj/contests/add")
        element = browser.find_element(By.XPATH, "//input[@name='contestIdAndName']")
        element.send_keys(contestId[-1])
        element = browser.find_element(By.XPATH, "//input[@value='Add']")
        element.click()
        time.sleep(1)
        element = browser.find_element(By.XPATH, "//input[@value='Yes']")
        element.click()
        time.sleep(5)
        browser.close()

        await msg_ctx.edit(content= f"團練賽已成功建立，請前往 codeforces 查看")

async def setup(client: commands.Bot):
    await client.add_cog(Round(client))