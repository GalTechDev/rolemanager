from system.lib  import *

import discord
Lib = Lib_UsOS()

app_version = "1.1"
role_folder = f"role_database.json"

class RoleDataBase:
    def __init__(self, path) -> None:
        self.path = path
        self.data={}

    def load_data(self):
        if not Lib.save.existe(self.path, ""):
            Lib.save.add_file(name=self.path)
            Lib.save.write(name=self.path, data=json.dumps({}))

        self.data = Lib.save.json_read(name=self.path)
        

    def save_data(self):
        Lib.save.write(name=self.path, data=json.dumps(self.data))

    def interaction_existe(self, interaction: discord.Interaction):
        if str(interaction.guild_id) in self.data.keys():
            if "custom_id" in interaction.data.keys():
                return str(interaction.data["custom_id"]) in self.data[str(interaction.guild_id)].keys()
        return False

    def add_role(self, guild: discord.Guild, view: discord.ui.View):
        if not str(guild.id) in self.data.keys():
            self.data.update({str(guild.id):{}})
        
        for select in view.children:
            if type(select)==Get_select:
                print(select.to_component_dict())
                self.data[str(guild.id)].update({str(select.custom_id):[str(option["value"]) for option in select.to_component_dict()["options"]]})
        print(self.data)
        self.save_data()


roleDB = RoleDataBase(role_folder)


#-------------------------------- View -----------------------------

async def valide_intaraction(interaction:discord.Interaction):
    try:
        await interaction.response.send_message()
    except Exception as error:
        pass
        #print(error)

class Creat_select_view(discord.ui.View):
    def __init__(self, guild: discord.Guild, timeout=180):
        super().__init__(timeout=timeout)
        i=0
        options=[]
        self.roles = []
        for key, role in guild._roles.items():
            options.append(discord.SelectOption(label=f"{role.name}", value=key))
            i+=1
            if i==25:
                i=0
                self.add_item(Creat_select(self.roles, options))
                options=[]
        if options!=[]:
            self.add_item(Creat_select(self.roles, options))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        view=Get_select_view(self.roles)
        await interaction.response.send_message(content='\u200b', view=view)
        roleDB.add_role(interaction.guild, view)
        await valide_intaraction(interaction)

class Creat_select(discord.ui.RoleSelect):
    def __init__(self, liste: list, options) -> None:
        super().__init__(placeholder=f"Choisi tes roles", max_values=len(options), min_values=0)
        self.roles = liste
        self.old = []

    async def callback(self, interaction: discord.Interaction):
        for roles in self.values:
            if roles not in self.old:
                self.roles.append(roles)
        for roles in self.old:
            if roles not in self.values:
                self.roles.remove(roles)

        self.old = self.values
        await valide_intaraction(interaction)

class Get_select_view(discord.ui.View):
    def __init__(self, roles, timeout=180):
        super().__init__(timeout=timeout)
        i=0
        options=[]
        for role in roles:
            options.append(discord.SelectOption(label=f"{role}", value=str(role.id)))
            i+=1
            if i==25:
                i=0
                self.add_item(Get_select(options))
                options=[]
        if options!=[]:
            self.add_item(Get_select(options))
        

class Get_select(discord.ui.Select):
    def __init__(self, options) -> None:
        super().__init__(placeholder=f"Choisi tes roles", max_values=len(options), min_values=0, options=options)
        

    async def callback(self, interaction: discord.Interaction):
        return  

#------------------------------ Event ------------------------------

@Lib.event.event()
async def on_ready():
    roleDB.load_data()

@Lib.event.event()
async def on_interaction(interaction: discord.Interaction):
    try:
        if roleDB.interaction_existe(interaction):
            await interaction.user.add_roles(*[interaction.guild.get_role(int(role)) for role in interaction.data["values"] if int(role) not in [user_role.id for user_role in interaction.user.roles]])
            await interaction.user.remove_roles(*[interaction.guild.get_role(int(int_role)) for int_role in roleDB.data[str(interaction.guild.id)][str(interaction.data["custom_id"])] if int_role not in interaction.data["values"]])
            await valide_intaraction(interaction)
    except Exception as error:
        print(error)

#------------------------------- Command ----------------------------

@Lib.app.slash(description="Ajoute un message pour choisir des roles")
async def add_role(ctx: discord.Interaction):
    try:
        await ctx.response.send_message(content="Select roles :", view=Creat_select_view(ctx.guild), ephemeral=True)
    except Exception as error:
        print(error)