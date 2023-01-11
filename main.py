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

    def edit_existe(self, interaction: discord.Interaction):
        if  not str(interaction.guild_id) in self.data.keys():
            return False
        try:
            for componment in self.data[str(interaction.guild_id)].values():
                if componment["edit_button"] == interaction.data["custom_id"]:
                    return True
        except Exception as error:
            print(error)
        return False

    def get_reponse_id(self, guild_id, button_id: str):
        for componment in self.data[str(guild_id)].values():
                if componment["edit_button"] == button_id:
                    return componment["reponse_id"]

    def remove_role(self, guild: discord.Guild, reponse_id: int):
        if not str(guild.id) in self.data.keys():
            return
        
        to_remove=[]
        for key, componment in self.data[str(guild.id)].items():
            if componment["reponse_id"]==reponse_id:
                to_remove.append(key)

        while to_remove!=[]:
            self.data[str(guild.id)].pop(to_remove.pop())

        self.save_data()
    
    def edit_role(self, guild: discord.Guild, view: discord.ui.View, reponse_id: int):
        if not str(guild.id) in self.data.keys():
            self.add_role(guild, view, reponse_id)
            return
        
        self.remove_role(guild, reponse_id)
        self.add_role(guild, view, reponse_id)


    def add_role(self, guild: discord.Guild, view: discord.ui.View, reponse_id: int):
        if not str(guild.id) in self.data.keys():
            self.data.update({str(guild.id):{}})
        
        for select in view.children:
            if type(select)==Get_select:
                self.data[str(guild.id)].update({select.custom_id:{"reponse_id":reponse_id, "edit_button":view.edit.custom_id,"values":[option["value"] for option in select.to_component_dict()["options"]]}})
        self.save_data()


roleDB = RoleDataBase(role_folder)


#-------------------------------- View -----------------------------

async def valide_intaraction(interaction:discord.Interaction):
    try:
        await interaction.response.send_message()
    except Exception as error:
        pass
        #print(error)

class Edit_select_view(discord.ui.View):
    def __init__(self, ctx: discord.Interaction , message: discord.Message, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.message = message
        self.roles = []
        self.add_item(Creat_select(self.roles))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        view=Get_select_view(self.roles)
        await self.ctx.delete_original_response()
        await self.message.edit(content='\u200b', view=view)
        roleDB.edit_role(interaction.guild, view, self.message.id)

    @discord.ui.button(label="Supprimer", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await self.ctx.delete_original_response()
        roleDB.remove_role(interaction.guild, self.message.id)
        await self.message.delete()


class Creat_select_view(discord.ui.View):
    def __init__(self, ctx: discord.Interaction ,timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.roles = []
        self.add_item(Creat_select(self.roles))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        view=Get_select_view(self.roles)
        await interaction.response.send_message(content='\u200b', view=view)
        await self.ctx.delete_original_response()
        reponse = await interaction.original_response()
        roleDB.add_role(interaction.guild, view, reponse.id)

class Creat_select(discord.ui.RoleSelect):
    def __init__(self, liste: list) -> None:
        super().__init__(placeholder=f"Choisi tes roles", max_values=25, min_values=0)
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
        self.edit = self.Edit_button(label="Edit")
        self.add_item(self.edit)

    class Edit_button(discord.ui.Button):
        def __init__(self, *, style: discord.ButtonStyle = discord.ButtonStyle.green, label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None):
            super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

        async def callback(self, interaction: discord.Interaction) -> Any:
            return


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
        if interaction.data["component_type"]==3:
            if roleDB.interaction_existe(interaction):
                await valide_intaraction(interaction)
                await interaction.user.add_roles(*[interaction.guild.get_role(int(role)) for role in interaction.data["values"] if int(role) not in [user_role.id for user_role in interaction.user.roles]])
                await interaction.user.remove_roles(*[interaction.guild.get_role(int(int_role)) for int_role in roleDB.data[str(interaction.guild.id)][str(interaction.data["custom_id"])]["values"] if int_role not in interaction.data["values"]])
                
        elif interaction.data["component_type"]==2:
            if Lib.is_in_staff(interaction):
                if roleDB.edit_existe(interaction):
                    reponse_id = roleDB.get_reponse_id(interaction.guild_id, interaction.data["custom_id"])
                    message = await interaction.channel.fetch_message(reponse_id)
                    await interaction.response.send_message(content="Select roles :", view=Edit_select_view(interaction, message), ephemeral=True)
                    await valide_intaraction(interaction)
            else:
                raise discord.app_commands.CheckFailure()
    except Exception as error:
        print(error)

#------------------------------- Command ----------------------------

@Lib.app.slash(description="Ajoute un message pour choisir des roles")
async def add_role(ctx: discord.Interaction):
    try:
        await ctx.response.send_message(content="Select roles :", view=Creat_select_view(ctx), ephemeral=True)
    except Exception as error:
        print(error)