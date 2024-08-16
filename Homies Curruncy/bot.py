'''
reseting role ids on last claim

'''



import os
#os.system("pip install aiohttp")
os.system("pip install google-generativeai")
import google.generativeai as genai

import discord
import aiohttp
import config
from discord.ext import commands, tasks
import json
from datetime import datetime, timezone
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
from collections import defaultdict
import shutil
from groq import Groq
import mysql.connector
import google.generativeai as generativeai
from google.generativeai.types import generation_types
from google.generativeai.types import HarmCategory, HarmBlockThreshold



intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True  # Needed to track member updates
bot = commands.Bot(command_prefix='+', intents=intents)
blocked_users = {}  # Dictionary to keep track of blocked users and their unblock time
spam_users = {}  # Dictionary to keep track of spam warnings
# Setup API keys for rotation
api_keys = [
    "AIzaSyA5dTvJDfmmUkQdFz1CYikzX2x0AmF8Ueo",
    "AIzaSyCS_MMYtXClAftcp5eTktMBZ1l-1m4-wo4",
    "yAIzaSyD2xoDSTq8ptIZF6Cix5sj3FK98FjCqtYo",
    "AIzaSyD2xoDSTq8ptIZF6Cix5sj3FK98FjCqtYo",
   
    # Add more keys as needed
]

current_key_index = 0
quota_usage = {key: 0 for key in api_keys}
max_quota_per_key = 1000  # Example limit

def get_next_api_key():
    global current_key_index

    # Optional: Check if current key is near its quota limit
    if quota_usage[api_keys[current_key_index]] >= max_quota_per_key:
        current_key_index = (current_key_index + 1) % len(api_keys)
    
    key = api_keys[current_key_index]
    current_key_index = (current_key_index + 1) % len(api_keys)
    return key

def log_quota_usage(api_key):
    quota_usage[api_key] += 1

def configure_genai():
    current_api_key = get_next_api_key()
    genai.configure(api_key=current_api_key)

configure_genai()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },



  # See https://ai.google.dev/gemini-api/docs/safety-settings
system_instruction=config.system_instruction

)
chat_session = config.ct_s



WEBHOOK_URL = config.webhook
bank = config.bank
mod = 1225751480842059776
headmod = 1227988469574533132
homiestaff = 1238105061943414784
owner = 1225899403655647344
admin = 1226126481235771463
admin_password = "00homies00"
log_channel_id = 1264048288743690331
del_channel_id = 1266303464279904337 # Replace with your log channel ID
block_user_1 = [1262767761659138070] ## Add zero in last 
DATA_FILE = 'data.json'
# Load or initialize the data from JSON file
roles = {
    "block": {"cost": 1000, "id": 123456789012345678},
    "gif": {"cost": 500, "id": 1228094136255647865},
    "VIP": {"cost": 5000, "id": 1237406055147900929},
    "Audit": {"cost": 3000, "id": 1263845122932740169},
    "Mute": {"cost": 3500, "id": 1263845384661372949},
    "Move": {"cost": 3000, "id": 1263845699842215956},
    "Timeout": {"cost": 70000, "id": 1263846234456592493},
    "Staff": {"cost": 10000, "id": 1238105061943414784},
    "omute": {"cost": 300, "id": 4136255647865}
}



######################### SQL TESTING #####################

# JSON file path
json_file_path = 'transactions.json'

# Function to read all transactions from JSON file
def read_all_from_json():
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []
    
    
def write_to_json(transaction):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    transaction['sr_no'] = len(data) + 1  # Assign serial number
    data.append(transaction)

    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Function to calculate total amount
def calculate_total_amount():
    transactions = read_all_from_json()
    total_amount = 0
    for transaction in transactions:
        if transaction['type'] == 'credit':
            total_amount += transaction['amount']
        elif transaction['type'] == 'debit':
            total_amount -= transaction['amount']
    return total_amount

# Function to write to MySQL
def write_to_mysql(transaction):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = "INSERT INTO transactions (type, amount, message) VALUES (%s, %s, %s)"
    values = (transaction['type'], transaction['amount'], transaction['message'])

    cursor.execute(query, values)
    connection.commit()
    
    cursor.close()
    connection.close()

# Function to read from JSON file
def read_from_json(sr_no):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            for transaction in data:
                if transaction.get('sr_no') == sr_no:
                    return transaction
    except FileNotFoundError:
        return None
    return None

# Function to read from MySQL
def read_from_mysql(sr_no):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM transactions WHERE id = %s"
    cursor.execute(query, (sr_no,))
    transaction = cursor.fetchone()

    cursor.close()
    connection.close()
    
    return transaction




















# Path to the JSON file
json_folder = 'jfile'
json_file = os.path.join(json_folder, 'bc.json')

# Ensure the folder exists
os.makedirs(json_folder, exist_ok=True)

# Function to load blacklisted channels from the JSON file
def load_blacklisted_channels():
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            return json.load(f)
    return {}

# Function to save blacklisted channels to the JSON file
def save_blacklisted_channels(data):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# Create a dictionary to store blacklisted channels
blacklisted_channels = load_blacklisted_channels()




######################## BLACKLIST END ######################3
SPAM_FILE = 'spammers.json'

def load_spam_data():
    if os.path.exists(SPAM_FILE):
        with open(SPAM_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_spam_data(data):
    with open(SPAM_FILE, 'w') as f:
        json.dump(data, f, indent=4)



def load_data():
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as f:
            json.dump({}, f)
    with open('data.json', 'r') as f:
        return json.load(f)

def fetch_user_ids():
    data = load_data()
    user_ids = list(data.keys())  # Extracts all the keys (user IDs) from the data dictionary
    return user_ids

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

async def log_transaction(message):
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        try:
            await log_channel.send(message)
        except discord.Forbidden:
            print("Bot does not have permission to send messages in the logs channel.")
        except discord.HTTPException as e:
            print(f"Failed to send message to logs channel: {e}")

       
    
async def delete_log(embed):
    log_channel = bot.get_channel(del_channel_id)
    if log_channel:
        try:
            await log_channel.send(embed=embed)  # Use embed=embed
        except discord.Forbidden:
            print("Bot does not have permission to send messages in the logs channel.")
        except discord.HTTPException as e:
            print(f"Failed to send message to logs channel: {e}")
            
      
    
    
    
    

@bot.command()
async def block(ctx, member: discord.Member, *, reason: str = None):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {'HC': 0}

    user_HC = data[user_id].get('HC', 0)

    # Debug: Print user's HC before deduction
    print(f"User {ctx.author} HC before deduction: {user_HC}")

    duration = 600
    if user_HC < 1000:
        embed = discord.Embed(title="You are poor", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Aww", value="You don't have enough HC", inline=True)
        await ctx.send(embed=embed)
        return

    data[user_id]['HC'] -= 1000
    save_data(data)
    # Debug: Print user's HC after deduction
    print(f"User {ctx.author} HC after deduction: {data[user_id]['HC']}")

    save_data(data)

    await log_transaction(f"{ctx.author.mention} has purchased the Temporary block for {member.mention}.")

    guild = ctx.guild
    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=True, speak=False)

    blocked_users[member.id] = {"unblock_time": discord.utils.utcnow().timestamp() + duration, "reason": reason}

    embed = discord.Embed(title="User Blocked", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Duration", value=f"{duration} seconds", inline=True)
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=True)
    await ctx.send(embed=embed)

    await asyncio.sleep(duration)

    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=None, speak=None)

    blocked_users.pop(member.id, None)

    embed = discord.Embed(title="User Unblocked", color=discord.Color.green())
    embed.add_field(name="User", value=member.mention, inline=True)
    await ctx.send(embed=embed)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    ##########################################################################################################
    
    
    
    
    
@tasks.loop(hours=24)
async def offline_penalty():
    data = load_data()
    current_time = datetime.now()

    for user_id, user_data in data.items():
        last_seen = datetime.fromisoformat(user_data.get('last_seen', current_time.isoformat()))
        
        if (current_time - last_seen).days >= 2:
            data[user_id]['HC'] = max(data[user_id]['HC'] - 100, 0)
            save_data(data)
            user = bot.get_user(int(user_id))
            if user:
                await user.send("You were offline for 2 days. 100 HC has been deducted from your account.")



# def sanitize_input(input_text):
#     # Replace or remove any content that could be considered inappropriate
#     sanitized_text = input_text.replace("offensive_word", "replacement")
#     return sanitized_text

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    data = load_data()

    # Initialize user data if not already present
    if user_id not in data:
        data[user_id] = {'last_seen': None, 'HC': 0}
        
    # Update last seen timestamp
    data[user_id]['last_seen'] = datetime.now().isoformat()

    # Handle DM messages
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        # Prepare the payload for the webhook
        payload = {
            "content": f"**Message from {message.author.name}#{message.author.discriminator} (ID: {message.author.id}):**\n{message.content}"
        }

        # Send the message to the server using the webhook
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status != 204:
                    print(f"Failed to send message to webhook. Status code: {response.status}")
        
        # Optionally, reply to the user in DMs
        #await message.channel.send("Your message has been forwarded to the server.")
        return  # Exit early since no further processing is needed for DM messages

    all_msg_channel_id = 1265782092382605422
    send_channel = bot.get_channel(all_msg_channel_id)

    ################## SPAM PROTECTION AND BLOCK #################
    block_info = blocked_users.get(message.author.id)
    if block_info:
        unblock_time = block_info.get("unblock_time")
        if unblock_time and discord.utils.utcnow().timestamp() < unblock_time:
            if not message.content.lower().startswith("sorry"):
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass  # Skip deletion if the bot doesn't have permission
                
                # Send DM to the blocked user
                try:
                    await message.author.send(
                        f"Your message was deleted because you are currently blocked from sending messages. "
                        f"If you believe this is a mistake, please use the correct format for unblocking."
						f"start with word sorry for example 'sorry I made a mistake', 'sorry I got blocked by this user' "
                    )
                except discord.Forbidden:
                    pass  # Skip DM if unable to send
                return
            else:
                # Check if the message contains the correct format
                blocker_mention = block_info.get("blocker_mention")
                if blocker_mention and blocker_mention not in message.content:
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        pass  # Skip deletion if the bot doesn't have permission
                    return

    # Load spam data if needed
    spam_data = load_spam_data()
    if user_id not in spam_users:
        spam_users[user_id] = {'count': 0, 'last_message_time': datetime.utcnow()}

    last_message_time = spam_users[user_id]['last_message_time']
    current_time = datetime.utcnow()

    # Spam protection logic
    if (current_time - last_message_time).seconds < 3:  # If message interval is less than 3 seconds
        spam_users[user_id]['count'] += 1
    else:
        spam_users[user_id]['count'] = 1  # Reset the count if interval is greater than 3 seconds

    spam_users[user_id]['last_message_time'] = current_time

    if spam_users[user_id]['count'] > 5:  # If user sends more than 5 messages in less than 3 seconds
        data[user_id]['HC'] = max(data[user_id].get('HC', 0) - 100, 0)
        save_data(data)

        embed = discord.Embed(title="Warning: Spam Detected", color=discord.Color.red())
        embed.add_field(name="User", value=message.author.mention, inline=True)
        embed.add_field(name="Action", value="100 HC deducted", inline=True)
        await message.channel.send(embed=embed)

        spam_users[user_id]['count'] = 0  # Reset the spam count
        if send_channel:
            await send_channel.send(f"User {message.author.mention} was detected spamming and had 100 HC deducted.")

        # Update spam history
        if user_id not in spam_data:
            spam_data[user_id] = {'spam_history': []}

        spam_data[user_id]['spam_history'].append({
            'timestamp': current_time.isoformat(),
            'message': message.content
        })
        save_spam_data(spam_data)
    #########################################################################

    specific_channel_id = 1264594660526129276
    if message.author.id in block_user_1:
        await message.delete()
        await message.channel.send(f"Hello {message.author.mention}! Gand mara na lovde.")
                
        # Send a DM to the user
        try:
            await message.author.send("You have been blocked from this server's channels for sending unauthorized messages. Please contact the admin for more details.")
        except discord.Forbidden:
            print(f"Could not send DM to {message.author.name}.")
        except discord.HTTPException as e:
            print(f"An error occurred while sending the DM: {e}")
        
        return

    # Handling specific channels
    if message.channel.id == 1266368080020373504:
        if message.content.startswith('+'):
            await bot.process_commands(message)
        else:
            # Create an embed for logging the deleted message
            embed = discord.Embed(title="Deleted Message", color=discord.Color.red())
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Message", value=message.clean_content, inline=True)

            # Log the embed
            await delete_log(embed)  # Ensure delete_log function accepts an embed parameter

            # Delete the message
            await message.delete()

            # Send a warning message
            await message.channel.send(f"{message.author.mention}, please do not send messages here.")
        return
     
    # Process commands if they start with the bot's prefix
    if message.content.startswith("+"):
        await bot.process_commands(message)
        return

    # Increment HC for non-command messages
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            'username': str(message.author),
            'HC': 0
        }

    # Increment HC for each message
    data[user_id]['HC'] += 1
    save_data(data)
    
    # Increment HC
    user_cache[user_id]['HC'] += 1
    update_user_cache(user_id, user_cache[user_id])
    

    # Ignore Tenor GIFs
    if any(
        attachment.url.lower().endswith(('.gif', '.mp4')) and 'tenor.com' in attachment.url.lower()
        for attachment in message.attachments
    ) or any(
        'tenor.com' in embed.url.lower()
        for embed in message.embeds
    ):
        return

    query = message.content.strip()

    if not query:
        return 

    # Check for @everyone or @here in the query
    if '@everyone' in query.lower() or '@here' in query.lower():
        await message.channel.send(
            "CantPingEveryone",
            allowed_mentions=discord.AllowedMentions.none()
        )
        return

    # --- Respond Only When Mentioned ---
    if bot.user.mentioned_in(message) or (message.reference and message.reference.message_id == bot.user.id):
        try:
            response = chat_session.send_message(query)
            response_text = response.text

            # Truncate the response if needed
            chunks = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
            for chunk in chunks:
                async with message.channel.typing():
                    await asyncio.sleep(2)  # Simulate a delay to show the typing animation
                    await message.channel.send(chunk)
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")
            print(f"Exception: {e}")

    await bot.process_commands(message)

    
    
    
    
    
    
    
    
@bot.event
async def on_ready():
    global user_cache
    user_cache = load_data()
    print(f'Logged in as {bot.user}')
    
    if not check_reminders.is_running():
        check_reminders.start() # Start the reminder and reset checks

    
@bot.command()
async def inr(ctx):
    def calculate_total_amount():
        try:
            with open('transactions.json', 'r') as f:
                transactions = json.load(f)
        except FileNotFoundError:
            return 0
        
        total_amount = 0
        for transaction in transactions:
            if transaction['type'] == 'credit':
                total_amount += transaction['amount']
            elif transaction['type'] == 'debit':
                total_amount -= transaction['amount']
        return total_amount

    total_amount = calculate_total_amount()

    embed = discord.Embed(
        title="Total Amount",
        description=f"Conversation Money Left is : {total_amount}rs",
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed)

    
    
@tasks.loop(hours=24)
async def check_reminders():
    now = datetime.now(timezone.utc)
    guild = bot.get_guild(1225746466346237982)  # Replace with your actual guild/server ID
    if not guild:
        return

    if now.day in [26, 28, 29,30]:
        channel = guild.get_channel(1266368080020373504)  # Replace with your actual channel ID
        if channel:
            await channel.send("# Hello All, HC reset is coming soon on the 1st of the next month. Please be prepared!")





@bot.command()
@commands.has_role('Admin')  # Replace 'admin' with the correct role name or ID
async def give(ctx):
    data = load_data()
    user_ids = fetch_user_ids()
    updated_count = 0

    for user_id in user_ids:
        if user_id in data:
            data[user_id]['HC'] = data[user_id].get('HC', 0) + 100
            updated_count += 1
            member = ctx.guild.get_member(int(user_id))
            if member:
                await ctx.send(f"HC for {member.mention} has been increased by 100.")
    
    save_data(data)
    await ctx.send(f"HC has been distributed to {updated_count} members with data.")

@give.error
async def give_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

        
        
        
        


        
@bot.command()
async def h(ctx):
    if ctx.channel.id == 1227470902388719666 :
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}, Do not use +h command here \n tere bap ka ghar nahi he homies curruncy ke channel pr use kar command")
    else:
        await ctx.send("""
            **Available Commands:**

**:scroll: Command List for Our Bot**

Hello everyone! Here's a list of commands you can use with our bot:

**1. `+stats`**
   - **Description**: Displays your current HC balance.

**2. `+userinfo [member]`**
   - **Description**: Shows information about a specified user (or yourself if no member is specified), including username and HC balance.

**3. `+roles [help]`**
   - **Description**: Lists available roles and their HC requirements. Add `help` for detailed information.

**4. `+shop [help]`**
   - **Description**: Shows available roles in the shop based on your HC balance. Add `help` for detailed information.

**5. `+allshop`**
   - **Description**: Lists all available roles and indicates if you can afford each role based on your HC balance.

**6. `+buy <role_name>`**
   - **Description**: Purchase a role with your HC. The role may be assigned immediately or processed by an admin.

**7. `+reset`**
   - **Description**: Resets HC for all users. Only available to the server owner or users with the 'Admin' role.

**8. `+donate <amount> <member>`**
   - **Description**: Donate HC to another member. Both users must have HC.

**9. `+admin <password> <amount> <recipient>`**
   - **Description**: Admin command to transfer HC to a recipient with a password verification.

**10. `+top <amount>`**
    - **Description**: Displays the top users by HC balance. For viewing 31 or more top users, a special message will be sent.

**11. `+block <member>`**
    - **Description**: Temporarily blocks a member from sending messages or speaking in voice channels for 10 minutes by spending 1000 HC.
.""")
    
    #await ctx.send(embed=embed)


@bot.command()
@commands.has_role(admin)
async def adminpanel(ctx):
    embed = discord.Embed(
        title="Admin Panel",
        description=(
            "+reset_hc - Reset HC for all users.\n"
            "+userinfo [member] - Get detailed info about a user.\n"
            "+set_hc <member> <amount> - Set HC for a user.\n"
            "+view_logs - View recent logs.\n"
        ),
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(admin)
async def reset_a(ctx):
    if ctx.message.author.id == ctx.guild.owner_id:
        # Define file paths
        data_file = 'data.json'  # Replace with your actual data file path
        backup_file = f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'  # Backup file name with timestamp

        # Create a backup of the current data file
        shutil.copy(data_file, backup_file)

        # Load data and reset HC
        data = load_data()
        for user_id in data:
            data[user_id]['HC'] = 0
        save_data(data)

        await ctx.send("All HC have been reset. A backup of the previous data has been created.")
        await log_transaction("All HC have been reset and backup created.")
    else:
        await ctx.send("You do not have permission to use this command.")
        
        
        
        
        
@bot.command()
@commands.has_role(admin)
async def set_hc(ctx, member: discord.Member, amount: int):
    data = load_data()
    user_id = str(member.id)
    if user_id in data:
        data[user_id]['HC'] = amount
        save_data(data)
        await ctx.send(f"HC for {member.mention} has been set to {amount}.")
    else:
        await ctx.send(f"User {member.mention} not found.")







@bot.command()
#@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member,  *, reason=None):
    data = load_data()
    user_id = str(ctx.author.id)
    user_HC = data.get(user_id, {}).get('HC', 0)


    if user_id not in data:
        data[user_id] = {'HC': 0}

    user_HC = data[user_id].get('HC', 0)

    # Debug: Print user's HC before deduction
    print(f"User {ctx.author} HC before deduction: {user_HC}")

    duration = 300
    if user_HC < 300:
        embed = discord.Embed(title="You are poor", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Aww", value="You don't have enough HC", inline=True)
        await ctx.send(embed=embed)
        return

    data[user_id]['HC'] -= 300
    save_data(data)
    # Debug: Print user's HC after deduction
    print(f"User {ctx.author} HC after deduction: {data[user_id]['HC']}")

    save_data(data)

    await log_transaction(f"{ctx.author.mention} has purchased the Temporary mute for {member.mention}.")

    guild = ctx.guild
    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=False, speak=False)

    embed = discord.Embed(title="User Muted", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Duration", value=f"{duration} seconds", inline=True)
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=True)
    await ctx.send(embed=embed)

    await asyncio.sleep(duration)

    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=None, speak=None)

    embed = discord.Embed(title="User Unmuted", color=discord.Color.green())
    embed.add_field(name="User", value=member.mention, inline=True)
    await ctx.send(embed=embed)
'''
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid duration. Please specify the duration in seconds.")
    else:
        await ctx.send("An error occurred while trying to mute the user.")
'''
@bot.command(name='unmute')
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    guild = ctx.guild
    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=None, speak=None)

    embed = discord.Embed(title="User Unmuted", color=discord.Color.green())
    embed.add_field(name="User", value=member.mention, inline=True)
    await ctx.send(embed=embed)

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to use this command.")




        
        
        
        
        
        
@bot.command()
@commands.has_any_role('Admin', 'Staff')
async def getdata(ctx):
    # Define the path to your configuration file
    config_file_path = 'data.json'  # Replace with your actual config file path

    try:
        # Send the file to the user's DM
        with open(config_file_path, 'rb') as file:
            await ctx.author.send(file=discord.File(file, 'data.json'))
        
        await ctx.send("The configuration file has been sent to your DM.")
    except discord.Forbidden:
        await ctx.send("I cannot send DMs to you. Please check your DM settings.")
    except FileNotFoundError:
        await ctx.send("The configuration file was not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

        
        
        
        
        
  
# Function to get or initialize a user's HC balance
def get_user_data(user_id):
    data = load_data()
    user_id_str = str(user_id)  # Ensure the user ID is a string for dictionary lookup
    if user_id_str not in data:
        data[user_id_str] = {"HC": 0}  # Initialize with default values if not found
        save_data(data)
    return data[user_id_str]

# Function to update a user's HC balance
def update_user_balance(user_id, amount):
    data = load_data()
    user_id_str = str(user_id)  # Ensure the user ID is a string for dictionary lookup
    if user_id_str in data:
        user_data = data[user_id_str]
        if "HC" in user_data:
            user_data["HC"] += amount
        else:
            user_data["HC"] = amount
        save_data(data)
    else:
        data[user_id_str] = {"HC": amount}
        save_data(data)

@bot.command(name='warn')
@commands.has_any_role('Admin', 'Homies Staff')
async def warn(ctx, member: discord.Member, *, reason: str = None):
    try:
        # Log the warning in a specific channel
        log_channel = bot.get_channel(1264048288743690331)  # Replace with your log channel ID
        if log_channel:
            await log_channel.send(f"{member.mention} has been warned for: {reason}")

        # Deduct 300 HC for the warning
        user_id = member.id
        user_data = get_user_data(user_id)
        current_balance = user_data.get("HC", 0)

        if current_balance >= 300:
            update_user_balance(user_id, -300)
            new_balance = get_user_data(user_id).get("HC", 0)
            await ctx.send(f"{member.mention} has been warned and 300 HC has been deducted. New balance: {new_balance} HC")
        else:
            await ctx.send(f"{member.mention} has been warned but does not have enough HC to deduct 300. Current balance: {current_balance} HC")

        # Send a DM to the warned user
        try:
            await member.send(f"You have been warned in {ctx.guild.name} for: {reason}. 300 HC has been deducted from your balance.")
        except discord.Forbidden:
            await ctx.send(f"{member.mention} has DMs disabled, cannot send warning message.")
        except discord.HTTPException as http_error:
            if http_error.status == 429:
                retry_after = int(http_error.headers.get('Retry-After', 0))
                await asyncio.sleep(retry_after)
                await member.send(f"You have been warned in {ctx.guild.name} for: {reason}. 300 HC has been deducted from your balance.")
            else:
                await ctx.send(f"Failed to send DM to {member.mention}. Please try again later.")

    except discord.Forbidden:
        await ctx.send("I do not have permission to warn members.")
    except discord.HTTPException as http_error:
        if http_error.status == 429:
            retry_after = int(http_error.headers.get('Retry-After', 0))
            await asyncio.sleep(retry_after)
            await warn(ctx, member, reason=reason)  # Retry the command
        else:
            await ctx.send("An error occurred while trying to warn the member.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member and a reason for the warning.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")









# Load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save data to file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize user cache
user_cache = load_data()

# Update user cache function
def update_user_cache(user_id, new_data):
    user_cache[user_id] = new_data
    save_data(user_cache)

@bot.command()
async def stats(ctx):
    user_id = str(ctx.author.id)

    if user_id in user_cache:
        HC = user_cache[user_id]['HC']
        await ctx.send(f'{ctx.author.mention} has {HC} HC.')
        print(f'{ctx.author} has {HC} HC.')
    else:
        await ctx.send(f'{ctx.author.mention} has no HC yet.')

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    if user_id in user_cache:
        user_data = user_cache[user_id]
        username = user_data['username']
        HC = user_data['HC']

        embed = discord.Embed(
            title=f"User Information: {member}",
            description=f"Details for {member.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Username", value=username, inline=False)
        embed.add_field(name="HC Balance", value=HC, inline=False)

        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="User Information",
            description=f"No information found for {member.mention}.",
            color=discord.Color.red()
        )
        async with ctx.typing():
            await ctx.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    user_id = str(after.id)
    if user_id in user_cache:
        # Update user cache with new data
        user_cache[user_id]['username'] = str(after)
        update_user_cache(user_id, user_cache[user_id])

        
        
        
        
        
        
        
        
        
        
    
@bot.command()
async def shop(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    user_HC = data.get(user_id, {}).get('HC', 0)
  
    roles_info = "Available roles in the shop:\n"
    for role_name, role_data in roles.items():
        cost = role_data["cost"]
        if user_HC >= cost:
            roles_info += f"{role_name} - {cost} HC (You can afford this)\n"
        #else:
           # roles_info += f"{role_name} - {cost} HC (You cannot afford this)\n"

    try:
        await ctx.send(roles_info)
    except discord.Forbidden:
        await ctx.send("I don't have permission to send messages in this channel.")

        
        
        
        
        
        
        
@bot.command()
async def allshop(ctx):
    data = load_data()  # Load user data
    user_id = str(ctx.author.id)
    user_HC = data.get(user_id, {}).get('HC', 0)

    roles_info = f"Your current HC: {user_HC}\nAll available roles:\n"
    for role_name, role_data in roles.items():
        cost = role_data["cost"]
        if user_HC >= cost:
            roles_info += f"{role_name} - {cost} HC (You can afford this)\n"
        else:
            roles_info += f"{role_name} - {cost} HC (You cannot afford this)\n"
      

    try:
        await ctx.send(roles_info)
        await ctx.send("Ask me if u want information about any role and there permission")
    except discord.Forbidden:
        await ctx.send("I don't have permission to send messages in this channel.")
        
        
        
        
        
        
        
        
        
        
        
        
@bot.command()
async def buy(ctx, role_name: str):
    data = load_data()
    user_id = str(ctx.author.id)

    # Check if user data exists
    if user_id not in data:
        await ctx.send("You don't have any HC yet.")
        return

    HC = data[user_id]['HC']

    # Normalize the role name to lowercase for matching
    role_name_normalized = role_name.lower()
    
    # Create a dictionary with lowercase keys for case-insensitive matching
    roles_lower = {key.lower(): value for key, value in roles.items()}

    # Check if role name is valid
    role_data = roles_lower.get(role_name_normalized)

    if role_data is None:
        valid_roles = ", ".join(roles.keys())
        await ctx.send(f"Invalid role name. Available roles are: {valid_roles}")
        return

    role_cost = role_data["cost"]
    role_id = role_data["id"]

    # Check if user has enough HC
    if HC < role_cost:
        await ctx.send(f"You don't have enough HC to buy the {role_name}.")
        return

    # Check if user already has the role
    role = ctx.guild.get_role(role_id)
    if role in ctx.author.roles:
        await ctx.send(f"You already have the {role_name} role.")
        return

    # Deduct HC and update data
    data[user_id]['HC'] -= role_cost
    save_data(data)

    # Notify admin
    admin_channel = bot.get_channel(log_channel_id)
    if admin_channel:
        await admin_channel.send(f"User {ctx.author} requested role: {role_name}. HC deducted: {role_cost}")

    # Assign the role to the user
    try:
        await ctx.author.add_roles(role)
        await ctx.send(f'Congratulations {ctx.author.mention}! You have purchased the {role_name} role.')
        print(f'{ctx.author.mention} has been assigned the {role_name} role.')
        await log_transaction(f'{ctx.author.mention} purchased the {role_name} role for {role_cost} HC.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to assign roles.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while assigning the role: {e}")

        
        
        
@bot.command(name='reset')
@commands.has_any_role('Admin')
async def reset(ctx):
    import shutil
    from datetime import datetime

    data_file = "data.json"
    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy(data_file, backup_file)
    
    data = load_data()
    for user_id, user_data in data.items():
        # Ensure 'protected_HC' is initialized if not present
        if 'protected_HC' not in user_data:
            user_data['protected_HC'] = 0

        # Apply the reset logic while preserving 30% of donated HC
        user_data['HC'] = user_data['protected_HC']
        user_data['protected_HC'] = 0  # Reset protected HC for the new month
    
    save_data(data)
    await ctx.send("HC has been reset. Backup has been created.")

    
@bot.command()
async def donate(ctx, amount: int, member: discord.Member):
    if amount <= 0:
        await ctx.send("Amount must be positive.")
        return

    data = load_data()
    donor_id = str(ctx.author.id)
    recipient_id = str(member.id)

    if donor_id not in data or recipient_id not in data:
        await ctx.send("Both users must have HC.")
        return

    if data[donor_id]['HC'] < amount:
        await ctx.send("You don't have enough HC to donate this amount.")
        return

    # Initialize or retrieve donation history for the donor
    if 'donation_history' not in data[donor_id]:
        data[donor_id]['donation_history'] = {}

    if recipient_id not in data[donor_id]['donation_history']:
        data[donor_id]['donation_history'][recipient_id] = []

    # Remove donations older than 7 days
    from datetime import datetime, timedelta
    current_time = datetime.now()
    one_week_ago = current_time - timedelta(days=7)

    data[donor_id]['donation_history'][recipient_id] = [
        donation for donation in data[donor_id]['donation_history'][recipient_id]
        if datetime.fromisoformat(donation['timestamp']) > one_week_ago
    ]

    # Calculate total donations in the last 7 days
    total_donated = sum(donation['amount'] for donation in data[donor_id]['donation_history'][recipient_id])

    if total_donated + amount > 1000:
        remaining_limit = 1000 - total_donated
        await ctx.send(f"You can only donate {remaining_limit} HC more to {member.mention} this week.")
        return

    # Update the HC for donor and recipient
    data[donor_id]['HC'] -= amount
    data[recipient_id]['HC'] += amount

    # Log the donation with a timestamp
    data[donor_id]['donation_history'][recipient_id].append({
        'amount': amount,
        'timestamp': current_time.isoformat()
    })

    # Add 30% of the donated amount to recipient's protected HC
    protected_amount = amount * 0.3
    if 'protected_HC' not in data[recipient_id]:
        data[recipient_id]['protected_HC'] = 0
    data[recipient_id]['protected_HC'] += protected_amount

    save_data(data)

    await ctx.send(f"You have donated {amount} HC to {member.mention}.")
    await log_transaction(f"{ctx.author} donated {amount} HC to {member.mention}.")

    
    
@bot.command()
@commands.has_role('Admin')
async def admin(ctx, password: str, amount: int, recipient: discord.Member):
    if password != admin_password:
        await ctx.send("Invalid password.")
        return

    data = load_data()
    admin_id = str(ctx.author.id)
    recipient_id = str(recipient.id)

    if admin_id not in data:
        await ctx.send("You don't have any HC yet.")
        return

    if recipient_id not in data:
        data[recipient_id] = {
            'username': str(recipient),
            'HC': 0
        }
        save_data(data)

    sender_HC = data[admin_id]['HC']

    # if sender_HC < amount:
    #     await ctx.send("You don't have enough HC to transfer that amount.")
    #     return

    if amount <= 0:
        await ctx.send("You need to specify a positive amount.")
        return

    #data[admin_id]['HC'] -= amount
    data[recipient_id]['HC'] += amount
    save_data(data)

    await ctx.send(f'{amount} HC have been transferred from {ctx.author.mention} to {recipient.mention}.')
    print(f'{ctx.author.mention} transferred {amount} HC to {recipient.mention}.')
    await log_transaction(f'{ctx.author.mention} transferred {amount} HC to {recipient.mention}.')

# Error handling for the command
@admin.error
async def setHC_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You need Admin permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

user_rank = list()
@bot.command()
async def top(ctx, amount: int):
    # Define roles to filter out (e.g., "headmod")
    roles_to_exclude = ["HEAD MOD"]
    minus_r = len(roles_to_exclude)+1
    amount+=minus_r

    if amount >= 29:
        await ctx.send(f"Seems like you want to see {amount} top users. Why not just view all the user data? Jhantu kahika soja bsdk")
        return

    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1].get('HC', 0), reverse=True)[:amount]

    leaderboard_lines = []

    for rank, (user_id, user_data) in enumerate(sorted_users, start=1):
        user = await bot.fetch_user(int(user_id))
        member = ctx.guild.get_member(int(user_id))

        # Check if the user has any of the roles to exclude
        if member and any(role.name.lower() in [r.lower() for r in roles_to_exclude] for role in member.roles):
            continue  # Skip users with the roles to exclude

        leaderboard_lines.append(f"{rank-minus_r}. {user.mention} - {user_data.get('HC', 0)} HC")

    leaderboard = "\n".join(leaderboard_lines)

    embed = discord.Embed(title=f"Top {amount-minus_r} Users by HC", color=discord.Color.red())
    embed.add_field(name="User", value=leaderboard, inline=False)

    await ctx.send(embed=embed)

    # Use logging instead of print for better control
    import logging
    logging.info("LEADERBOARD command executed")

    


async def block(ctx,name:discord.Member):
    data = load_data()
    user_id = str(ctx.author.id)
    user_HC = data.get(user_id, {}).get('HC', 0)


    if user_id not in data:
        data[user_id] = {'HC': 0}

    user_HC = data[user_id].get('HC', 0)

    # Debug: Print user's HC before deduction
    print(f"User {ctx.author} HC before deduction: {user_HC}")

    duration = 600
    if user_HC < 1000:
        embed = discord.Embed(title="You are poor", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Aww", value="You don't have enough HC", inline=True)
        await ctx.send(embed=embed)
        return

    data[user_id]['HC'] -= 1000
    save_data(data)
    # Debug: Print user's HC after deduction
    print(f"User {ctx.author} HC after deduction: {data[user_id]['HC']}")

    save_data(data)

    await log_transaction(f"{ctx.author.mention} has purchased the Temporary block for {member.mention}.")

    guild = ctx.guild
    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=False, speak=False)

    embed = discord.Embed(title="User Blocked", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Duration", value=f"{duration} seconds", inline=True)
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=True)
    await ctx.send(embed=embed)

    await asyncio.sleep(duration)

    for channel in guild.channels:
        await channel.set_permissions(member, send_messages=None, speak=None)

    embed = discord.Embed(title="User Unblock", color=discord.Color.green())
    embed.add_field(name="User", value=member.mention, inline=True)
    await ctx.send(embed=embed)
    
    
    
    
@bot.command()
@commands.has_role('Admin')  # or replace with 'Staff' if applicable
async def notify_all(ctx):
    message = "Hello everyone! A new command has been added to the bot. Come and check it on HOMIES server"

    # Notify all members in the server
    for member in ctx.guild.members:
        if not member.bot:  # Ensure not to DM bots
            try:
                await member.send(message)
                print(f"Sent DM to {member}")
            except discord.Forbidden:
                print(f"Failed to send DM to {member}.")
            except Exception as e:
                print(f"An error occurred while sending DM to {member}: {e}")

    await ctx.send("DMs have been sent to all users.")
    
    
    

# Command to blacklist a channel
@bot.command()
@commands.has_permissions(administrator=True)  # Only allow admins to blacklist
async def blacklist(ctx, channel: discord.TextChannel):
    if str(channel.id) not in blacklisted_channels:
        blacklisted_channels[str(channel.id)] = "all"
        save_blacklisted_channels(blacklisted_channels)
    await ctx.send(f'{channel.mention} has been blacklisted from using commands.')

# Command to unblacklist a channel
@bot.command()
@commands.has_permissions(administrator=True)  # Only allow admins to unblacklist
async def unblacklist(ctx, channel: discord.TextChannel):
    if str(channel.id) in blacklisted_channels:
        del blacklisted_channels[str(channel.id)]
        save_blacklisted_channels(blacklisted_channels)
        await ctx.send(f'{channel.mention} has been unblacklisted.')

# Check if the channel is blacklisted
@bot.check
async def cbc(ctx):
    if str(ctx.channel.id) in blacklisted_channels:
        return False
    return True

# Error handler for blacklisted channels
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Commands are blacklisted in this channel.')



    
@bot.command()
async def uchc(ctx):
    user_data = load_data()
    total_users = len(user_data)
    total_hc = sum(user['HC'] for user in user_data.values())
    await ctx.send(f"Total Users: {total_users}\nTotal HC: {total_hc}")
    

    
    

def load_user_ids():
    try:
        with open('user_ids.json', 'r') as file:
            user_ids = json.load(file)
    except FileNotFoundError:
        user_ids = []
    return user_ids

    
@bot.command()
async def userid(ctx):
    user_ids = fetch_user_ids()
    print(user_ids)
    await ctx.send(f"User IDs: {', '.join(user_ids)}")

    
    
    
    

@bot.command()
@commands.has_permissions(administrator=True)
async def debit(ctx, amount: int, *, msg: str):
    global bank
    bank -= amount
    transaction = {'type': 'debit', 'amount': amount, 'message': msg}
    
    # Store transaction in JSON
    write_to_json(transaction)
    
    # Update total amount
    total_amount = calculate_total_amount()
    
    await ctx.send(f"Debited {amount}. Total balance: {bank} for {msg}. Total amount: {total_amount}")

@bot.command()
@commands.has_permissions(administrator=True)
async def credit(ctx, amount: int, *, msg: str):
    global bank
    bank += amount
    transaction = {'type': 'credit', 'amount': amount, 'message': msg}
    
    # Store transaction in JSON
    write_to_json(transaction)
    
    # Update total amount
    total_amount = calculate_total_amount()
    
    await ctx.send(f"Credited {amount}. Total balance: {bank} for {msg}. Total amount: {total_amount}")

@bot.command()
async def view(ctx, sr_no: int):
    transaction = read_from_json(sr_no)
    
    if not transaction:
        transaction = read_from_mysql(sr_no)
    
    if transaction:
        await ctx.send(f"Transaction {sr_no}: {transaction['type']} {transaction['amount']} for {transaction['message']}")
    else:
        await ctx.send(f"No transaction found with serial number {sr_no}")


        
        
        
        

# Function to read all transactions from JSON file
def read_all_from_json():
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []

@bot.command()
@commands.has_permissions(administrator=True)
async def allt(ctx, page: int = 1):
    transactions = read_all_from_json()
    transactions_per_page = 10
    total_pages = (len(transactions) + transactions_per_page - 1) // transactions_per_page
    
    if page > total_pages or page < 1:
        await ctx.send(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
        return
    
    start_index = (page - 1) * transactions_per_page
    end_index = min(start_index + transactions_per_page, len(transactions))
    page_transactions = transactions[start_index:end_index]
    
    embed = discord.Embed(title=f"Transactions - Page {page}/{total_pages}", color=discord.Color.blue())
    
    for transaction in page_transactions:
        embed.add_field(
            name=f"Transaction {transaction['sr_no']}",
            value=f"Type: {transaction['type']}\nAmount: {transaction['amount']}\nMessage: {transaction['message']}",
            inline=False
        )
    
    message = await ctx.send(embed=embed)
    
    # Adding reactions for pagination
    if total_pages > 1:
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == '◀️':
                if page > 1:
                    page -= 1
                else:
                    continue
            elif str(reaction.emoji) == '▶️':
                if page < total_pages:
                    page += 1
                else:
                    continue
            
            start_index = (page - 1) * transactions_per_page
            end_index = min(start_index + transactions_per_page, len(transactions))
            page_transactions = transactions[start_index:end_index]
            
            embed = discord.Embed(title=f"Transactions - Page {page}/{total_pages}   ", color=discord.Color.blue())
            
            for transaction in page_transactions:
                embed.add_field(
                    name=f"Transaction {transaction['sr_no']} ",
                    value=f"Type: {transaction['type']}\nAmount: {transaction['amount']}\nMessage: {transaction['message']}",
                    inline=False
                )
            
            await message.edit(embed=embed)
            await message.remove_reaction(reaction.emoji, ctx.author)
        
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break
    
    

    

@bot.command()
async def trend(ctx):
    transactions = read_all_from_json()
    last_total = 0
    increasing = None

    for transaction in transactions:
        if transaction['type'] == 'credit':
            last_total += transaction['amount']
        elif transaction['type'] == 'debit':
            last_total -= transaction['amount']

        if increasing is None:
            increasing = last_total > 0
        elif (last_total > 0) != increasing:
            await ctx.send(f"The total amount trend has changed at transaction {transaction['sr_no']}.")
            return

    trend_status = "increasing" if increasing else "decreasing"
    await ctx.send(f"The total amount is currently {trend_status}.")

    
@bot.command(name='mass_dm')
@commands.has_any_role('Admin')
async def mass_dm(ctx, user_ids: str, *, msg: str):
    user_ids = user_ids.split(',')
    for user_id in user_ids:
        try:
            user = await bot.fetch_user(int(user_id.strip()))
            await user.send(msg)
            await ctx.send(f"Message sent to {user.mention}.")
        except discord.NotFound:
            await ctx.send(f"User with ID {user_id} not found.")
        except discord.Forbidden:
            await ctx.send(f"Cannot send message to {user_id}.")
        except Exception as e:
            await ctx.send(f"An error occurred while messaging {user_id}: {e}")


    
    
@bot.command()
@commands.has_any_role('Admin',".")
async def mdm(ctx, x:int, user_ids: str, *, msg: str):
    user_ids = user_ids.split(',')
    import time
    for user_id in user_ids:
        try:
            for i in range(x):
                #time.sleep(1)
                user = await bot.fetch_user(int(user_id.strip()))
                await user.send(msg)
                await ctx.send(f"Message sent to {user.mention}.")
        except discord.NotFound:
            await ctx.send(f"User with ID {user_id} not found.")
        except discord.Forbidden:
            await ctx.send(f"Cannot send message to {user_id}.")
        except Exception as e:
            await ctx.send(f"An error occurred while messaging {user_id}: {e}")



    

@bot.command()
@commands.has_role('Admin')
async def s(ctx, *, msg: str):
    channel_id = 1227470902388719666  # Replace with your specific channel ID
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(msg)
        await ctx.send(f"Message sent to {channel.mention}")
    else:
        await ctx.send("Channel not found.")


@bot.command()
@commands.has_permissions(administrator=True)
async def ss(ctx, channel_id: int, *, msg: str):
    # Try to get the channel
    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("Channel not found.")
        return

    # Send the message to the channel
    await channel.send(msg)
    await ctx.send(f"Message sent to channel <#{channel_id}> .")

    


@bot.event
async def on_member_update(before, after):
    user_id = after.id
     # Ignore if the prefix is [AFK]
    if after.display_name.startswith("[AFK]") or after.name.startswith("[AFK]"):
        return
    if before.display_name.startswith("[AFK]") or before.name.startswith("[AFK]"):
        return
    if before.display_name != after.display_name:
        print(f'User ID: {user_id} | {before.display_name} changed their nickname to {after.display_name}')
        await notify_user(f'User ID: <@{user_id}> |   {before.display_name} changed their nickname to {after.display_name}')

    if before.name != after.name:
        print(f'User ID: {user_id} | {before.name} changed their username to {after.name}')
        await notify_user(f'User ID: <@{user_id}> |   {before.name} changed their username to {after.name}')

    if before.activities != after.activities:
        before_bio = next((activity.state for activity in before.activities if isinstance(activity, discord.CustomActivity)), None)
        after_bio = next((activity.state for activity in after.activities if isinstance(activity, discord.CustomActivity)), None)

        if before_bio != after_bio:
            print(f'User ID: {user_id} | {before.name} changed their bio to: {after_bio}')
            await notify_user(f'User ID: <@{user_id}> |   {before.name} changed their bio to: {after_bio}')

async def notify_user(message, attempt=1):
    channel = bot.get_channel(1272268858341855336)  # Replace with your notification channel ID
    try:
        await channel.send(message)
        await asyncio.sleep(1)  # Delay to avoid hitting rate limits (adjust as needed)
    except discord.errors.HTTPException as e:
        print(f"HTTP Exception: {e}")
        if e.status == 429:
            retry_after = min(2 ** attempt, 60)  # Exponential backoff with a cap of 60 seconds
            await asyncio.sleep(retry_after)
            await notify_user(message, attempt + 1)

    
    
    
    
    
    
    
    
    
    
'''
reaction on img in meadia

'''
@bot.command(name='media')
async def media(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        file = discord.File(fp=await attachment.read(), filename='media.png')

        # Send the media and create a message with the attachment
        message = await ctx.send("React to this message to earn HC!", file=file)

        # Add reaction emojis
        reactions = ['👍', '❤️', '😂', '😮', '😢', '😡']  # Add any reactions you want to use
        for reaction in reactions:
            await message.add_reaction(reaction)

        # Wait for reactions
        def check(reaction, user):
            return reaction.message.id == message.id and user != ctx.author

        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=86400, check=check)
                if user.id != ctx.author.id:  # Exclude the uploader's reactions
                    # Increase HC by 10 per reaction
                    user_data = get_user_data(user.id)
                    update_user_balance(user.id, 10)
            except asyncio.TimeoutError:
                await ctx.send("Time is up! The media post is no longer accepting reactions.")
                break
    else:
        await ctx.send("Please attach an image with your command.")
 
    
    
    
    







    
bot.run(config.mytoken)



