import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.sinks import MP3Sink
import asyncio

from langchain_funcs import *

load_dotenv()

DISCORD_TOKEN=os.getenv('DISCORD_KEY')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='pa ', intents=intents, help_command=None)

@bot.event
async def on_ready():
    # Bot presence
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="pa record"))
    

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
    
@bot.command(name = 'record', description = "Records 3s clip of voice of user", pass_context=True)
async def record(ctx:commands.Context):
    
    loading_msg = await ctx.send("Loading...")
    bot_voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    connect_flag, message = await join(ctx, bot_voice=bot_voice, loading_msg=loading_msg, called=True)
    bot_voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not connect_flag:
        loading_msg.edit(content=message)
    
    author_id = ctx.author.id
    sink = MP3Sink()
    
    async def finished_recording(sink):
        
        audio = sink.audio_data[author_id]
   
        with open(f'{author_id}.mp3', 'wb') as f:
            f.write(audio.file.read())
        await ctx.send(f"Processing voice for {ctx.author.mention}")
        
        prompt = await user_prompt_from_audio(f"{author_id}.mp3", perform_function_call=False, delete_after=True)
    
        await ctx.send(f"You said, {prompt}")
        # is this correct
        
        await function_call_from_user_prompt(prompt)
        
    bot_voice.start_recording(sink, finished_recording)
    await ctx.send("Started recording!")
    
    bot.loop.create_task(stop_recording_after_delay(bot_voice, ctx, 3))
    
async def stop_recording_after_delay(vc, ctx, delay):
    await asyncio.sleep(delay)
    vc.stop_recording()
    await ctx.send(f"Recording stopped after {delay} seconds!")
    
bot.run(DISCORD_TOKEN)