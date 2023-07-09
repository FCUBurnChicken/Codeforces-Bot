import discord
from discord.ext import commands
from discord import app_commands
import requests
import json
import typing
import random
import settings
import enum
from utils import cf_api


tags = typing.Literal["constructive algorithms","data structures", "dfs and similar", "divide and conquer", 
    "dp", "dsu", "geometry","graphs", "hashing", "interactive", "implementation", "math", "matrices", 
    "number theory", "probabilities", "shortest paths", "sortings", 
    "string suffix structures", "strings", "trees","two pointers"]

cf = cf_api.Codeforces_API()
url = "https://codeforces.com/api"

class User(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    def get_user_info(self, handle):
        response = requests.get(url + "/user.info?handles=" + handle)
        response = json.loads(response.text)
        return {
            'handle': handle,
            'rating': response['result'][0]['rating'],
            'maxRating': response['result'][0]['maxRating'],
            'rank': response['result'][0]['rank'],
            'maxRank': response['result'][0]['maxRank']
        }

    @commands.hybrid_command()
    async def user(self, ctx, handle: str):
        res = self.get_user_info(handle)
        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.set_author(name=f"User {ctx.author.display_name}'s Handle", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="This is Footer")
        embed.add_field(name="Handle", value=f"{res['handle']}", inline=False)
        embed.add_field(name="Rating / MaxRating", value=f"{res['rating']}/{res['maxRating']}", inline=False)
        embed.add_field(name="Rank / MaxRank", value=f"{res['rank']}/{res['maxRank']}", inline=False)
        await ctx.send(embed = embed)
    
    @commands.hybrid_command(name="show-solved-problems")
    async def show_solved_problems(self, ctx, handle: str):
        user_problems = await cf.get_user_problems(handle)
        problem_name = []
        problem_rating = []
        for user_problem in user_problems[1]:
            problem_name.append(f"[{user_problem.name}](https://codeforces.com/contest/{user_problem.id}/problem/{user_problem.index})")
            problem_rating.append(str(user_problem.rating))

        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Problem", value="\n".join(problem_name[:5]), inline=True)
        embed.add_field(name="Rating", value="\n".join(problem_rating[:5]), inline=True)
        await ctx.send(embed = embed)

    async def fetch(self, ctx, problem_list, user_problems, low, high):
        flag = True
        while flag:
            flag = False
            problem = problem_list[random.randrange(len(problem_list))]
            if problem['rating'] > high or problem['rating'] < low:
                flag = True
            else: 
                for user_problem in user_problems[1]:
                    if user_problem.name == problem['name']:
                        print(f"{problem['name']} has been solved")
                        flag = True
                        break

        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.set_author(name=f"User {ctx.author.display_name}'s Handle", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="This is Footer")
        embed.add_field(name="Problem", value=f"[{problem['name']}](https://codeforces.com/contest/{problem['contestId']}/problem/{problem['index']})", inline=True)
        embed.add_field(name="Rating", value=f"{problem['rating']}", inline=True)
        return embed

    @commands.hybrid_command(name="fetch-problems")
    async def fetch_problems(self, ctx: commands.Context, tag: tags, low: int, high: int):
        user_problems = await cf.get_user_problems("YuKai00")
        with open(settings.ALL_PROBLEMS) as f:
            all_problems = json.load(f)
        problem_list = await cf.classify_problems(all_problems, tag)

        await ctx.send(embed=(await self.fetch(ctx, problem_list, user_problems, low, high)), ephemeral=True)

        
async def setup(client):
    await client.add_cog(User(client))