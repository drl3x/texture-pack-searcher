import discord
from discord import app_commands
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Use environment variable in hosting

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


@tree.command(name="search", description="Search for a texture pack")
@app_commands.describe(name="Name of the texture pack")
async def search(interaction: discord.Interaction, name: str):
    await interaction.response.defer()

    # 1️⃣ Search Discord server messages
    for channel in interaction.guild.text_channels:
        try:
            async for message in channel.history(limit=200):
                if name.lower() in message.content.lower():
                    await interaction.followup.send(
                        f"Found in #{channel.name}:\n{message.jump_url}"
                    )
                    return
        except:
            continue

    # 2️⃣ Search Modrinth API
    async with aiohttp.ClientSession() as session:
        url = f"https://api.modrinth.com/v2/search?query={name}&facets=[[\"project_type:resourcepack\"]]"
        async with session.get(url) as resp:
            data = await resp.json()

            if data["hits"]:
                project = data["hits"][0]
                link = f"https://modrinth.com/resourcepack/{project['slug']}"
                await interaction.followup.send(
                    f"Found on Modrinth:\n{project['title']}\n{link}"
                )
                return

    await interaction.followup.send("Texture pack not found.")
    

client.run(TOKEN)
