from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.sinks import MP3Sink, AudioData
import asyncio
import os
import stt

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='pa ', intents=intents, help_command=None)

@bot.event
async def on_ready():
    # Bot presence
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="pa help"))

@bot.command(name = 'join', description = "Joins your voice channel", aliases=['connect'], pass_context=True)
async def join(ctx:commands.Context, bot_voice=None, loading_msg=None, called=False):

    if loading_msg is None:
        loading_msg = await ctx.send("Loading...")

    # getting bot's voice channel object
    bot_voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # if user not in VC
    if ctx.author.voice is None:
        await loading_msg.edit(content = "You are not connected to a voice channel.")
        return False, "You are not connected to a voice channel."
    
    # if bot not in VC but author in VC
    elif bot_voice is None and ctx.author.voice:
        await loading_msg.edit(content=f"Joining {ctx.author.voice.channel}!")
        await ctx.author.voice.channel.connect()
        return True, "Success"

    # if author and bot in same VC but wasnt called by another function
    elif ctx.author.voice.channel == bot_voice.channel and not called:
        await loading_msg.edit(content = "Already in your voice channel!")
        return True, "Success"
    
    elif ctx.author.voice.channel == bot_voice.channel and called:
        return True, "Success"

    # if bot and author in different VCs
    elif ctx.author.voice.channel != bot_voice.channel and ctx.author.voice:
        await loading_msg.edit(content = "Bot already in another voice channel!")
        return False, "Bot already in another voice channel!"
    

@bot.command(name="record", pass_context=True)
async def record(ctx:commands.Context):
    bot_voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    connect_flag, message = await join(ctx, bot_voice=bot_voice, called=True)
    ctx.voice_client.start_recording(MP3Sink(), finished_callback, ctx)

async def finished_callback(sink, ctx):

    for user_id, audio in sink.audio_data.items():
        file = discord.File(audio.file, f"{user_id}.{sink.encoding}")
        transcript = stt.process_from_audio_data(file.fp.read(), 'raw')
        await ctx.channel.send(f"Transcript for {user_id}: {transcript}") 

@bot.command(name='stop', pass_context=True)
async def stop(ctx:commands.Context):
    ctx.voice_client.stop_recording()


bot.run(DISCORD_TOKEN)