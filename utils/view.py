import discord
import json 

with open('selection.json') as f:
    data = json.load(f)
    data['tags'].sort()

class MyViews(discord.ui.View):
    def __init__(self, timeout = 180):
        super().__init__(timeout=timeout)
        self.tags_select = []
        self.tags_select1 = []
        self.tags_select2 = []
    
    @discord.ui.select(
        placeholder = "選擇題目類型",
        min_values = 1,
        max_values = 5,
        options = [discord.SelectOption(label = data['tags'][index]) for index in range(0, 25)],
        custom_id="select_callback1"
    )
    async def select_callback1(self, interaction, select):
        self.tags_select1 = select.values
        await interaction.response.defer()

    @discord.ui.select(
        placeholder = "選擇題目類型",
        min_values = 1,
        max_values = 5,
        options = [discord.SelectOption(label = data['tags'][index]) for index in range(25, len(data['tags']))],
        custom_id="select_callback2"
    )
    async def select_callback2(self, interaction, select):
        self.tags_select2 = select.values
        await interaction.response.defer()

    @discord.ui.button(
        label="確認",
        style=discord.ButtonStyle.success,
        custom_id="confirm_button"
    )
    async def confirm_button(self, interaction, button):
        self.tags_select = self.tags_select1 + self.tags_select2
        self.stop()

class YesNoViews(discord.ui.View):
    def __init__(self, timeout = 180):
        super().__init__(timeout=timeout)
        self.result = []

    @discord.ui.button(
        label="✔", 
        style=discord.ButtonStyle.success,
        custom_id="ok_button"
    )
    async def ok_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = True
        self.stop()

    @discord.ui.button(
        label="❌",
        style=discord.ButtonStyle.success,
        custom_id="notok_button"
    )
    async def notok_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = False
        self.stop()
