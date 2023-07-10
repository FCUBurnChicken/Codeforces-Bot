import discord
from discord.ext import commands
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

    @commands.hybrid_command()
    async def user(self, ctx: commands.Context, handle: str):
        res = cf.get_user_info(handle)
        embed = discord.Embed(color=discord.Color.dark_magenta())
        embed.set_author(name=f"User {ctx.author.display_name}'s Handle", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="This is Footer")
        embed.add_field(name="Handle", value=f"{res['handle']}", inline=False)
        embed.add_field(name="Rating / MaxRating", value=f"{res['rating']}/{res['maxRating']}", inline=False)
        embed.add_field(name="Rank / MaxRank", value=f"{res['rank']}/{res['maxRank']}", inline=False)
        await ctx.send(embed = embed)
        
async def setup(client: commands.Bot):
    await client.add_cog(User(client))