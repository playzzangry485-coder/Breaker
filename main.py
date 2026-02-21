import discord
from discord.ext import commands
import yt_dlp
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="+", intents=intents)

@bot.event
async def on_ready():
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

    ydl_opts = {"format": "bestaudio", "quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info["url"]

    source = discord.FFmpegPCMAudio(
        stream_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    vc.stop()
    vc.play(source)

    await ctx.send(f"Now Playing: {info['title']}")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("TOKEN"))
