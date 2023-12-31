import settings
import traceback
from discord.ext import commands
from utils import cf_api
from data import connect

cf = cf_api.Codeforces_API()
conn = connect.Connect()

async def update_problemset(client: commands.Bot):
    logging_channel = await client.fetch_channel(settings.LOGGING_CHANNEL)
    await logging_channel.send("Attempting to update problemset...")
    problem_id = [x[0] for x in conn.get_all_problems()]
    problem_id.sort(reverse=True)
    problem_list = await cf.get_problem_list()

    prob_cnt = 0
    
    try:
        for problem in problem_list:
            if 'rating' in problem:
                if problem["contestId"] not in problem_id:
                    prob_cnt += 1
                    conn.add_problem(problem["contestId"], problem["index"], problem["name"], problem["rating"], problem["tags"])
                else:
                    break
        await logging_channel.send(f"Problemset Updated, added {prob_cnt} new problems")
    except Exception as e:
        await logging_channel.send(f"Error while updating problemset: {str(traceback.format_exc())}")

async def update_handle(client: commands.Bot):
    logging_channel = await client.fetch_channel(settings.LOGGING_CHANNEL)
    await logging_channel.send("Attempting to update handles...")
    handles = conn.get_all_handle()
    users = [user.display_name for user in client.users]
    
    handle_cnt = 0

    try:
        for handle in handles:
            if handle[1] in users:
                data = await cf.get_user_info(handle[2])
                if data["handle"] != handle[2] or data["rating"] != handle[3] or data["rank"] != handle[4] or data["titlePhoto"] != handle[5] :
                    handle_cnt += 1
                    conn.change_handle(data['handle'], data['rating'], data["rank"], data['titlePhoto'], handle[1], handle[0])
        await logging_channel.send(f"Handles Updated, update {handle_cnt} handles")
    except Exception as e:
        await logging_channel.send(f"Error while updating problemset: {str(traceback.format_exc())}")