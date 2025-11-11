import discord # Imports the discord.py library, which is used to interact with the Discord API.
from discord.ext import commands # Imports the 'commands' extension from discord.py, useful for creating bot commands.
import logging # Imports the logging module for handling log messages.
from dotenv import load_dotenv # Imports the load_dotenv function from the python-dotenv library to load environment variables.
import os # Imports the os module, which provides a way of using operating system dependent functionality, like accessing environment variables.
from discord.ext.commands import DefaultHelpCommand # Imports the DefaultHelpCommand class from the discord.ext.commands module, which provides the default help command for the bot.

load_dotenv() # Loads environment variables from a .env file into the script's environment.
token = os.getenv('DISCORD_TOKEN') # Retrieves the bot's token from the environment variables, which is necessary for the bot to log in.

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # Configures a file handler for logging, directing logs to 'discord.log' in UTF-8 encoding, overwriting the file each time.
intents = discord.Intents.default() # Creates a default set of Discord intents, which define what events the bot wants to receive from Discord.
intents.message_content = True # Enables the message content intent, allowing the bot to read the content of messages. This is often required for command processing.
intents.members = True # Enables the members intent, allowing the bot to receive information about guild members (e.g., when they join or leave).
intents.guilds = True # Enables guild-related events like bans, roles, etc.

bot = commands.Bot(command_prefix='!', intents=intents) # Creates a bot instance using the commands extension, setting the command prefix to '!'.

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}") # Prints a message to the console, indicating that the bot is ready to go.

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to the server {member.name}") # Sends a welcome message to the newly joined member.
    except discord.Forbidden:
        print(f"Couldn't DM {member.name}") # Avoids crashing if DMs are closed.
    channel = discord.utils.get(member.guild.text_channels, name="welcome") # Looks for a channel named "general" in the server.
    if channel:
        await channel.send(f"Welcome to the server {member.name}")
    else:
        print("Channel not found")

swear_words = ["shit", "bitch", "fuck", "asshole", "dick", "pussy"]
@bot.event
async def on_message(message):
    if message.author == bot.user: # Checks if the message was sent by the bot itself. To avoid infinite loop
        return

    if any(word in message.content.lower() for word in swear_words): # Checks if any of the swear words are in the message
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")
    await bot.process_commands(message) # Passes the message to the bot for command processing.

@bot.command() 
async def hello(ctx):   # !hello command
    await ctx.send(f"Hello {ctx.author.mention}!")

secret_role = "Gamer"

@bot.command()
async def assign(ctx): # !assign command
    role = discord.utils.get(ctx.guild.roles, name=secret_role) # Finds the role with the name "Gamer"

    if role:
        await ctx.author.add_roles(role) # Adds the role to the user
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}") # Sends a confirmation message to the channel 
    else:
        await ctx.send("Role doesn't exist") # Sends an error message to the channel

@bot.command()  
async def remove(ctx): # !remove command
    role = discord.utils.get(ctx.guild.roles, name=secret_role) # Finds the role with the name "Gamer"

    if role:
        await ctx.author.remove_roles(role) # Removes the role from the user
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} role removed") # Sends a confirmation message to the channel
    else:
        await ctx.send("Role doesn't exist") # Sends an error message to the channel

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
    await ctx.author.send(f"You said: {msg}") # Sends a DM to the user

@bot.command()
async def reply(ctx): # !reply command
    await ctx.reply("This is a reply to your message!") # Sends a reply to the message

@bot.command()
async def poll(ctx, *, question): # !poll command
    embed = discord.Embed(title="New Poll", description=question) # Creates an embed for the poll
    poll_message = await ctx.send(embed=embed) # Sends the embed to the channel
    await poll_message.add_reaction("👍") # Adds reactions to the poll
    await poll_message.add_reaction("👎") # Adds reactions to the poll

@bot.command()
async def count(ctx): 
    await ctx.send(f"Total members in {ctx.guild.name}: {ctx.guild.member_count}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int): # !clear command
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None): # !kick command
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} has been kicked from the server.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None): # !ban command
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} has been banned from the server.")
    
@bot.command()
@commands.has_permissions(ban_members=True)  # Ensures the user has permission to ban/unban members
async def unban(ctx, member: discord.User):  # !unban command that takes only a mentioned user (@User)
    """Unbans a user by mentioning them (example: !unban @User)."""
    banned_users = await ctx.guild.bans()  # Fetches the list of all banned users from the server
    
    for ban_entry in banned_users:  # Loops through each banned user entry
        user = ban_entry.user  # Gets the user object from the ban entry
        
        if user.id == member.id:  # Compares the mentioned user ID with the banned user's ID
            await ctx.guild.unban(user)  # Unbans the matched user from the server
            await ctx.send(f"✅ Unbanned {user.mention}")  # Sends a success message mentioning the unbanned user
            return  # Stops the function after successfully unbanning
    
    await ctx.send("❌ User not found in ban list.")  # Sends an error message if the mentioned user isn’t in the ban list

@bot.command()
async def avatar(ctx, member: discord.Member = None): # !avatar command
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

@bot.command()
async def ping(ctx): # !ping command
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def say(ctx, *, message): # !say command
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def embed(ctx, *, message): # !embed command
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)

@bot.command()
async def role(ctx, *, role: discord.Role): # !role command
    await ctx.send(f"Role: {role.name}\nID: {role.id}")

@bot.command()
async def server(ctx): # !server command
    await ctx.send(f"Server name: {ctx.guild.name}\nTotal members: {ctx.guild.member_count}")

@bot.command()
async def user(ctx, *, user: discord.User = None): # !user command
    user = user or ctx.author
    await ctx.send(f"Username: {user.name}\nID: {user.id}")

@bot.command(name="bot")  # still responds to !bot
async def bot_info(ctx):  # function name is different
    await ctx.send(f"Bot name: {bot.user.name}\nID: {bot.user.id}")

@bot.command()
async def roll(ctx, dice: str): # !roll command
    """Roll dice in NdN format, like 2d6.""" 
    import random  # Imports random for generating random numbers
    try:
        rolls, limit = map(int, dice.split('d'))  # Splits input like '2d6' into number of dice and sides
    except ValueError:
        await ctx.send("Use format NdN (like 2d6)")  # Sends a message if format is wrong
        return  # Stops the function if invalid format
    results = [random.randint(1, limit) for _ in range(rolls)]  # Rolls the dice
    await ctx.send(f"{ctx.author.mention} rolled: {', '.join(map(str, results))} (Total: {sum(results)})")  # Sends the roll result

@bot.command()
async def choose(ctx, *options): # !choose command
    """Randomly choose between given options."""
    import random  # Imports random for random selection
    if not options:  # Checks if no options were provided
        await ctx.send("You need to give me some options!")  # Warns user if no options
    else:
        await ctx.send(f"I choose: {random.choice(options)} 🎲")  # Picks and sends one random option

@bot.command()
async def quote(ctx): # !quote command
    """Send a random motivational quote."""
    import random  # Imports random for random quote selection
    quotes = [  # List of motivational quotes
        "Believe you can and you're halfway there.",
        "Keep your face always toward the sunshine—and shadows will fall behind you.",
        "Don’t watch the clock; do what it does. Keep going.",
        "The harder you work for something, the greater you'll feel when you achieve it."
    ]
    await ctx.send(random.choice(quotes))  # Sends a random quote

@bot.command()
async def serverinfo(ctx): # !serverinfo command
    """Displays info about the server."""
    guild = ctx.guild  # Gets the current server object
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())  # Creates an embed for server info
    embed.add_field(name="Owner", value=guild.owner, inline=True)  # Adds owner info
    embed.add_field(name="Region", value=guild.preferred_locale, inline=True)  # Adds server region
    embed.add_field(name="Members", value=guild.member_count, inline=True)  # Adds member count
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)  # Adds total number of roles
    if guild.icon:  # Checks if server has an icon
        embed.set_thumbnail(url=guild.icon.url)  # Sets the icon as embed thumbnail
    await ctx.send(embed=embed)  # Sends the embed message

@bot.command()
async def userinfo(ctx, member: discord.Member = None): # !userinfo command
    """Shows user info."""
    member = member or ctx.author  # Defaults to command author if no member provided
    embed = discord.Embed(title=f"User Info - {member.name}", color=discord.Color.green())  # Creates an embed for user info
    embed.add_field(name="ID", value=member.id)  # Adds user ID
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))  # Adds join date
    embed.add_field(name="Status", value=str(member.status).title())  # Adds current status
    embed.set_thumbnail(url=member.avatar.url)  # Sets user's avatar as thumbnail
    await ctx.send(embed=embed)  # Sends the embed message

@bot.command()
@commands.has_permissions(manage_roles=True)  # Checks if the user has role management permissions
async def mute(ctx, member: discord.Member, *, reason=None): # !mute command
    """Temporarily mute a member."""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")  # Looks for 'Muted' role in the server
    if not mute_role:  # Checks if role exists
        await ctx.send("No 'Muted' role found.")  # Warns if missing
        return  # Stops function
    await member.add_roles(mute_role, reason=reason)  # Adds 'Muted' role to the user
    await ctx.send(f"{member.mention} has been muted.")  # Confirms mute

@bot.command()
@commands.has_permissions(manage_roles=True)  # Checks if user can manage roles
async def unmute(ctx, member: discord.Member): # !unmute command
    """Unmute a member."""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")  # Looks for 'Muted' role
    if mute_role in member.roles:  # Checks if user has muted role
        await member.remove_roles(mute_role)  # Removes the mute role
        await ctx.send(f"{member.mention} has been unmuted.")  # Confirms unmute
    else:
        await ctx.send("This user is not muted.")  # Warns if user isn’t muted

@bot.command()
async def joke(ctx): # !joke command
    """Fetches a random joke from JokeAPI."""
    import requests  # Imports requests to fetch data from API
    res = requests.get("https://v2.jokeapi.dev/joke/Any?type=single")  # Requests a random joke
    if res.status_code == 200:  # Checks if request succeeded
        data = res.json()  # Converts response to JSON
        await ctx.send(data['joke'])  # Sends the joke
    else:
        await ctx.send("Couldn't fetch a joke right now!")  # Warns if API failed

@bot.command()
async def coinflip(ctx): # !coinflip command
    """Simulates a coin toss."""
    import random  # Imports random for coin toss
    result = random.choice(["Heads 🪙", "Tails 🪙"])  # Chooses between heads or tails
    await ctx.send(f"{ctx.author.mention} flipped: {result}")  # Sends result

@bot.command()
async def eightball(ctx, *, question): # !8ball command
    """Magic 8-ball style answers."""
    import random  # Imports random for responses
    responses = [  # List of 8-ball responses
        "Yes.", "No.", "Maybe.", "Definitely!", "Absolutely not.",
        "Ask again later.", "I’m not sure.", "Without a doubt.", "It’s possible.", "Don’t count on it."
    ]
    await ctx.send(f"🎱 {random.choice(responses)}")  # Sends a random response

@bot.command()
async def remindme(ctx, time: str, *, task: str): # !remindme command
    """Set a reminder after a specific time (e.g. !remindme 10s drink water)."""
    import asyncio  # Imports asyncio for sleep/timer functionality
    unit = time[-1]  # Extracts the last character (s, m, or h)
    amount = time[:-1]  # Extracts the number part
    try:
        amount = int(amount)  # Converts number to integer
    except ValueError:
        await ctx.send("Please specify time correctly (e.g. 10s, 5m, 2h).")  # Warns if time format invalid
        return  # Stops function

    if unit == "s":  # If seconds
        delay = amount
    elif unit == "m":  # If minutes
        delay = amount * 60
    elif unit == "h":  # If hours
        delay = amount * 3600
    else:
        await ctx.send("Invalid time unit! Use s, m, or h (e.g. 10s, 5m, 1h).")  # Warns invalid unit
        return  # Stops function

    await ctx.send(f"⏰ Reminder set for {time} to: {task}")  # Confirms reminder set
    await asyncio.sleep(delay)  # Waits for specified time
    await ctx.send(f"⏰ {ctx.author.mention}, reminder: {task}")  # Sends reminder after waiting

class MyHelpCommand(commands.HelpCommand):  # Creates a custom help command class
    async def send_bot_help(self, mapping):  # Called when user runs just !help
        embed = discord.Embed(title="🤖 Bot Command Help", color=discord.Color.blurple())  # Creates a help embed
        embed.description = "Here’s a list of all available commands and how to use them.\nUse `!help <command>` for detailed info on a specific command."  # Sets embed description

        for cog, commands_list in mapping.items():  # Loops through all command groups
            filtered = await self.filter_commands(commands_list, sort=True)  # Filters out commands the user can’t run
            command_signatures = [self.get_command_signature(c) for c in filtered]  # Gets syntax for each command
            if command_signatures:  # If there are any commands in the list
                embed.add_field(  # Adds a field to the embed with command names
                    name="📘 General Commands" if cog is None else cog.qualified_name,
                    value="\n".join(command_signatures),
                    inline=False
                )

        channel = self.get_destination()  # Gets the channel to send the message to
        await channel.send(embed=embed)  # Sends the embed to the Discord channel

    async def send_command_help(self, command):  # Called when user runs !help <command>
        embed = discord.Embed(title=f"ℹ️ Help for `{command.name}`", color=discord.Color.green())  # Creates an embed for individual command help
        embed.add_field(name="Description", value=command.help or "No description provided.", inline=False)  # Adds command description
        embed.add_field(name="Usage", value=f"`{self.clean_prefix}{command.name} {command.signature}`", inline=False)  # Shows usage format
        channel = self.get_destination()  # Gets the channel to send to
        await channel.send(embed=embed)  # Sends embed with help info

# Replace default help command with the custom one
bot.help_command = MyHelpCommand()  # Sets our custom help command for the bot
bot.help_command.cog = None  # Ensures it works outside any specific cog

bot.run(token, log_handler=handler, log_level=logging.DEBUG) # Runs the bot with the provided token, setting the log handler to 'handler' and the log level to 'DEBUG'.
