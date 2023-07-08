import discord
from discord.ext import commands
from discord import app_commands
import requests
import json

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
    
    def get_AC_problem(self, handle):
        response = requests.get(url + "/user.status?handle=" + handle).text
        response = json.loads(response)
        problem = []
        for i in range(len(response['result'])):
            if response['result'][i]['verdict'] == 'OK' and [response['result'][i]['problem']['name'], response['result'][i]['problem']['rating'],response['result'][i]['problem']['tags']] not in problem:
                problem.append([response['result'][i]['problem']['name'], response['result'][i]['problem']['rating'],response['result'][i]['problem']['tags']])
        return problem

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
        
async def setup(client):
    await client.add_cog(User(client))