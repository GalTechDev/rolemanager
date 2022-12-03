from system.lib  import *
import app.rolemanager as RoleManager

Lib = lib.Lib_UsOS()

app_version = "1.1"
role_folder = f"{classbot_folder}/role_database.json"
role_db = RoleManager(role_folder)

def __init__(bot_client):
    global client
    client=bot_client
    init_event()


#------------ Func -----------------
async def addrole(ctx, role_: discord.Role, emote): #aliases=["addmention", "addemoji", "addemote"]
    try:
        refId = ctx.message.reference.message_id
    except Exception:
        await ctx.channel.send("Erreur! Pas de message lié!")
        return

    try:
        role = role_.name
    except Exception:
        await ctx.channel.send("Erreur! Role inexistant")
        return

    emote = emote

    commu = ctx.guild.id
    chat = ctx.channel.id

    guild_info = client.get_guild(int(commu))
    channel = guild_info.get_channel(int(chat))
    role_message = await channel.fetch_message(int(refId))

    try:
        await role_message.add_reaction(emote)
    except Exception:
        await ctx.channel.send("Erreur! Mauvaise emote!")
        return

    await role_db.bind(commu, chat, refId, emote, role)
    role_db.save(role_db.role_database)

    channel = guild_info.get_channel(int(chat))
    role_message = await channel.fetch_message(ctx.message.id)
    await role_message.add_reaction("✅")
    await ctx.channel.purge(limit=1)


async def removerole(ctx, role: discord.Role):

    try:
        refId = ctx.message.reference.message_id
    except Exception:
        await ctx.channel.send("Erreur! Pas de message lié!")
        return

    role_name = role.name
    commu = ctx.guild.id
    chat = ctx.channel.id

    guild_info = client.get_guild(int(commu))

    try:
        role_db.remove_role(commu, chat, refId, role_name)
    except Exception:
        await ctx.channel.send("Erreur! Role inexistant")
        return

    role_db.save(role_db.role_database)

    channel = guild_info.get_channel(int(chat))
    role_message = await channel.fetch_message(ctx.message.id)
    await role_message.add_reaction("✅")
    await ctx.channel.purge(limit=1)


async def removeemote(ctx, emote):

    try:
        refId = ctx.message.reference.message_id
    except Exception:
        await ctx.channel.send("Erreur! Pas de message lié!")
        return

    role_name = emote
    commu = ctx.guild.id
    chat = ctx.channel.id

    guild_info = client.get_guild(int(commu))

    try:
        role_db.remove_emote(commu, chat, refId, role_name)
    except Exception:
        await ctx.channel.send("Erreur! Emote inexistant")
        return

    role_db.save(role_db.role_database)

    channel = guild_info.get_channel(int(chat))
    role_message = await channel.fetch_message(ctx.message.id)
    await role_message.add_reaction("✅")
    await ctx.channel.purge(limit=1)

# -------------------------------- SLASH COMMANDE -------------------------------


@Lib.app.slash(name="addrole", description="liste des commande", guild=discord.Object(id=649021344058441739))
async def addrole_slash(ctx: discord.Interaction, role: discord.Role, emote: str, message_id: int):
    if not Lib.is_in_staff(ctx, True):
        await ctx.response.send_message(content="Vous n'avez pas les permissions pour utiliser cette commande.", ephemeral=True)
        return

    refId = message_id
    role = role.name
    commu = ctx.guild.id
    chat = ctx.channel.id

    guild_info = client.get_guild(int(commu))
    channel = guild_info.get_channel(int(chat))
    message = ""
    try:
        role_message = await channel.fetch_message(int(refId))
        try:
            await role_message.add_reaction(emote)
        except Exception:
            message+="Erreur! Mauvaise emote!\n"
    except Exception:
        message+="Erreur! message_id invalide!\n"
    finally:
        if message != "":
            await ctx.response.send_message(message, ephemeral=True)
            return

    await role_db.bind(commu, chat, refId, emote, role)
    role_db.save(role_db.role_database)
    await ctx.response.send_message(f"{role} à bien été créé avec l'emote {emote}.", ephemeral=True)


@Lib.app.slash(name="removerole", description="retire le role", guild=discord.Object(id=649021344058441739))
async def removerole_slash(ctx: discord.Interaction, role: discord.Role, message_id:int):
    if not Lib.is_in_staff(ctx, True):
        await ctx.response.send_message("Vous n'avez pas les permissions pour utiliser cette commande.", ephemeral=True)
        return

    refId = message_id
    role_name = role.name
    commu = ctx.guild.id
    chat = ctx.channel.id
    guild_info = client.get_guild(int(commu))
    channel = guild_info.get_channel(int(chat))

    try:
        role_message = await channel.fetch_message(int(refId))
    except Exception:
        await ctx.response.send_message("Erreur! message_id invalide!", ephemeral=True)

    try:
        role_db.remove_role(commu, chat, refId, role_name)
    except Exception:
        await ctx.response.send_message("Erreur! Role inexistant", ephemeral=True)
        return

    role_db.save(role_db.role_database)
    await ctx.response.send_message(f"{role} à bien été retiré du message.", ephemeral=True)


@Lib.app.slash(name="removeemote", description="retir l'emote", guild=discord.Object(id=649021344058441739))
async def removeemote_slash(ctx: discord.Interaction, emote: str, message_id: int):
    if not Lib.is_in_staff(ctx, True):
        await ctx.send("Vous n'avez pas les permissions pour utiliser cette commande.", ephemeral=True)
        return

    refId = message_id
    role_name = emote
    commu = ctx.guild.id
    chat = ctx.channel.id
    guild_info = client.get_guild(int(commu))
    channel = guild_info.get_channel(int(chat))

    try:
        role_message = await channel.fetch_message(int(refId))
    except Exception:
        await ctx.response.send_message("Erreur! message_id invalide!", ephemeral=True)

    try:
        await role_message.clear_reaction(emote)
        role_db.remove_emote(commu, chat, refId, role_name)
    except Exception:
        await ctx.response.send_message("Erreur! Emote inexistant", ephemeral=True)
        return

    role_db.save(role_db.role_database)
    await ctx.response.send_message(f"{emote} à bien été retiré du message.", ephemeral=True)

# ---------------------------------- EVENTS ------------------------------------

def init_event():
    @Lib.client.event
    async def on_raw_reaction_add(ctx):
        if ctx.user_id == client.user.id:
            return

        message_id = str(ctx.message_id)
        chat_id = ctx.channel_id
        guild_id = ctx.guild_id
        # print(ctx.emoji.name)

        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        user = await guild.fetch_member(ctx.user_id)

        val = role_db.is_binded_from_emote(guild_id, chat_id, message_id, ctx.emoji.name)

        if val:
            role = discord.utils.get(guild.roles, name=val)
            await user.add_roles(role)


    @Lib.client.event
    async def on_raw_reaction_remove(ctx):
        if ctx.user_id == client.user.id:
            return

        guild_id = ctx.guild_id

        # guild_id = 550450730192994306
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        user = await guild.fetch_member(ctx.user_id)

        val = role_db.is_binded_from_emote(guild_id, ctx.channel_id, ctx.message_id, ctx.emoji.name)

        if val:
            role = discord.utils.get(guild.roles, name=val)
            await user.remove_roles(role)