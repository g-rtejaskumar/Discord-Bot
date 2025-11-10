import discord # Imports the discord.py library, which is used to interact with the Discord API.
from discord.ext import commands # Imports the 'commands' extension from discord.py, useful for creating bot commands.
import logging # Imports the logging module for handling log messages.
from dotenv import load_dotenv # Imports the load_dotenv function from the python-dotenv library to load environment variables.
import os # Imports the os module, which provides a way of using operating system dependent functionality, like accessing environment variables.

load_dotenv() # Loads environment variables from a .env file into the script's environment.
token = os.getenv('DISCORD_TOKEN') # Retrieves the bot's token from the environment variables, which is necessary for the bot to log in.

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # Configures a file handler for logging, directing logs to 'discord.log' in UTF-8 encoding, overwriting the file each time.
intents = discord.Intents.default() # Creates a default set of Discord intents, which define what events the bot wants to receive from Discord.
intents.message_content = True # Enables the message content intent, allowing the bot to read the content of messages. This is often required for command processing.
intents.members = True # Enables the members intent, allowing the bot to receive information about guild members (e.g., when they join or leave).

bot = commands.Bot(command_prefix = '!', intents=intents) # Creates a bot instance using the commands extension, setting the command prefix to '!'.

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}") # Prints a message to the console, indicating that the bot is ready to go.

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}") # Sends a welcome message to the newly joined member.

swear_words = ["shit", "bitch", "fuck", "asshole", "dick", "pussy"]
@bot.event
async def on_message(message):
    if message.author == bot.user: # Checks if the message was sent by the bot itself. To avoid infinite loop
        return

    if any(word in message.content.lower() for word in swear_words): # Checks if any of the swear words are in the message
        await message.delete()
        await message.channel.send(f"{message.author.mention} - dont use that word!")
    await bot.process_commands(message) # Passes the message to the bot for command processing.

@bot.command() 
async def hello(ctx):   # !hello command
    await ctx.send(f"Hello {ctx.author.mention}!")

secret_role = "Gamer"
@bot.command()
async def assign(ctx): #!role command
    role = discord.utils.get(ctx.guild.roles, name = secret_role) # Finds the role with the name "Gamer"

    if role:
        await ctx.author.add_roles(role)    # Adds the role to the user
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}") # Sends a confirmation message to the channel 
    else:
        await ctx.send("Role dosen'nt exist") # Sends an error message to the channel

@bot.command()  
async def remove(ctx): # !remove command
    role = discord.utils.get(ctx.guild.roles, name = secret_role) # Finds the role with the name "Gamer"

    if role:
        await ctx.author.remove_roles(role) # Removes the role from the user
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed") # Sends a confirmation message to the channel
    else:
        await ctx.send("Role dosen'nt exist") # Sends an error message to the channel

@bot.command()
@commands.has_role(secret_role) # Checks if the user has the role "Gamer"
async def secret(ctx): # !secret command
    await ctx.send("Welcome to the club!")

@secret.error
async def secret_error(ctx, error): # Handles the error if the user doesn't have the role
    if isinstance(error, commands.MissingRole): # Checks if the error is due to missing role
        await ctx.send("You do not have permission to do that!") # Sends an error message

@bot.command()
async def dm(ctx, *, msg): # !dm command
    await ctx.author.send(f"You said {msg}") # Sends a DM to the user

@bot.command()
async def reply(ctx): # !reply command
    await ctx.reply("This is a reply to your message!") # Sends a reply to the message

@bot.command()
async def poll(ctx, *, question): # !poll command
    embed = discord.Embed(title = "New Poll", description = question)    # Creates an embed for the poll
    poll_message = await ctx.send(embed = embed) # Sends the embed to the channel
    await poll_message.add_reaction("👍")    # Adds reactions to the poll
    await poll_message.add_reaction("👎")    # Adds reactions to the poll

bot.run(token, log_handler = handler, log_level = logging.DEBUG) # Runs the bot with the provided token, setting the log handler to 'handler' and the log level to 'DEBUG'.