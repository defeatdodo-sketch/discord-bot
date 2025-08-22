import discord
from discord.ext import commands, tasks
import os, json, time

# ---- Intents ----
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# ---- Bot ----
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")  # sera défini sur Render

# ---- stockage expirations : {guild_id: {user_id: timestamp}} ----
DATA_FILE = "shields.json"
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
def save_data(d):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f)
    except Exception:
        pass
data = load_data()

async def ensure_role(guild: discord.Guild) -> discord.Role:
    role = discord.utils.get(guild.roles, name="Bouclier")
    if role is None:
        role = await guild.create_role(name="Bouclier", reason="Rôle bouclier 24h")
    return role

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne ✅")
    check_expirations.start()

@tasks.loop(seconds=60)
async def check_expirations():
    now = time.time()
    changed = False
    for guild in bot.guilds:
        g = data.get(str(guild.id), {})
        if not g:
            continue
        role = discord.utils.get(guild.roles, name="Bouclier")
        to_delete = []
        for user_id, expire_at in g.items():
            if now >= expire_at:
                member = guild.get_member(int(user_id))
                if member and role in member.roles:
                    try: await member.remove_roles(role, reason="Bouclier expiré (24h)")
                    except: pass
                to_delete.append(user_id)
        for uid in to_delete:
            del g[uid]
            changed = True
        if g: data[str(guild.id)] = g
        else: data.pop(str(guild.id), None)
    if changed: save_data(data)

# -------- Slash command : /item (buy bouclier) --------
@bot.slash_command(name="item", description="Acheter des objets")
async def item(
    ctx: discord.ApplicationContext,
    action: discord.Option(str, choices=["buy"]),
    objet:  discord.Option(str, choices=["bouclier"])
):
    if action == "buy" and objet == "bouclier":
        role = await ensure_role(ctx.guild)

        # Donne le rôle + enregistre l'expiration
        await ctx.author.add_roles(role, reason="Achat bouclier (24h)")
        expire_at = time.time() + 24*3600
        guild_map = data.get(str(ctx.guild_id), {})
        guild_map[str(ctx.author.id)] = expire_at
        data[str(ctx.guild_id)] = guild_map
        save_data(data)

        # Réponse (ephemeral = visible seulement par l’acheteur)
        await ctx.respond("🛡️ Bouclier acheté ! Protection active pendant 24h.", ephemeral=True)

bot.run(TOKEN)
