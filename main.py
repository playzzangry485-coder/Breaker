import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import os
import subprocess
# Ensure ffmpeg is installed via mise
subprocess.run("mise install ffmpeg", shell=True)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")


@bot.command()
async def music(ctx, *, url):
    if not ctx.author.voice:
        await ctx.send("Join a voice channel first!")
        return

    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        vc = await channel.connect()
    else:
        vc = ctx.voice_client

    await ctx.send("Loading music... 🎵")

    ydl_opts = {"format": "bestaudio", "quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info["url"]

    source = discord.FFmpegPCMAudio(
    stream_url,
    executable="./bin/ffmpeg",  # path to your ffmpeg binary
    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    options="-vn"
    )

    if vc.is_playing():
        vc.stop()

    vc.play(source)

    await ctx.send(f"Now Playing: {info['title']}")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@tree.command(name="play", description="Play music from YouTube")
@app_commands.describe(url="YouTube URL")
async def slash_play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Join a voice channel first!")
        return

    channel = interaction.user.voice.channel

    if interaction.guild.voice_client:
        vc = interaction.guild.voice_client
    else:
        vc = await channel.connect()

    await interaction.response.send_message("Loading music... 🎵")

    ydl_opts = {"format": "bestaudio", "quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info["url"]

    source = discord.FFmpegPCMAudio(
        stream_url,
        executable="ffmpeg",
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    if vc.is_playing():
        vc.stop()

    vc.play(source)


@tree.command(name="leave", description="Disconnect the bot")
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected 👋")
    else:
        await interaction.response.send_message("Not in a voice channel.")


bot.run(os.getenv("TOKEN"))
