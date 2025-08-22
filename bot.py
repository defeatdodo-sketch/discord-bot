import discord
from discord.ext import commands, tasks
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")  # On va mettre ton token dans Railway (pas ici)

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne !")

@bot.slash_command(name="item")
async def item(ctx, action: str, objet: str):
    if action == "buy" and objet == "bouclier":
        role = discord.utils.get(ctx.guild.roles, name="Bouclier")
        if not role:
            role = await ctx.guild.create_role(name="Bouclier")
        
        await ctx.author.add_roles(role)
        await ctx.respond("🛡️ Bouclier acheté ! Tu l’as pour 24h.")

        # Retirer après 24h
        await asyncio.sleep(86400)  
        await ctx.author.remove_roles(role)
        await ctx.respond("⏳ Ton bouclier a expiré !")
        
bot.run(TOKEN)
