import os

from dotenv import load_dotenv

load_dotenv()

#### Load Env ####
# for UnbelievaBoat API
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
UNBELIEVABOAT_TOKEN = os.getenv("UNBELIEVABOAT_TOKEN")

# for Discord API
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID_UNBELIEVABOAT_DISP =  os.getenv("DISCORD_CHANNEL_ID_UNBELIEVABOAT_DISP")
