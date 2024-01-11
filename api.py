from mojang import API
from hypixel import HypixelException
from hypixel.errors import GuildNotFound, PlayerNotFound
import os, uuid, hypixel, asyncio, json
from dotenv import load_dotenv

load_dotenv()
mojang = API()

def get_uuid(username: str) -> str:
	try:
		return str(uuid.UUID(mojang.get_uuid(username)))
	except:
		return None

async def check_stats(uuid: str) -> hypixel.Player:
	client = hypixel.Client(os.getenv('HYPIXEL_API_KEY'))

	async with client:
		try:
			return await client.player(uuid)
		except PlayerNotFound:
			return None
		except HypixelException:
			return False
	
async def check_guild(username: str) -> hypixel.Guild:
	client = hypixel.Client(os.getenv('HYPIXEL_API_KEY'))

	async with client:
		try:
			return await client.guild_from_player(username)
		except GuildNotFound:
			return None

async def id_guild(id: str) -> hypixel.Guild:
	client = hypixel.Client(os.getenv('HYPIXEL_API_KEY'))

	async with client:
		try:
			return await client.guild_from_id(id)
		except GuildNotFound:
			return None

def compare_usernames(dcUsername: str, hypixelUsername: str):
	try:
		dcUsername = dcUsername.removesuffix('#0')
		hypixelUsername = hypixelUsername.removesuffix('#0')
		if '#' in dcUsername and '#' in hypixelUsername:
			#legacyUsername = True
			return dcUsername == hypixelUsername
		return dcUsername.lower() == hypixelUsername.lower()
	except:
		return None
	
def write_to_db(discord_id: int, minecraft_uuid: str):
	data = {str(discord_id): minecraft_uuid}
	with open('db.json', 'r') as f:
		previous = json.load(f)
	with open('db.json', 'w') as f:
		json.dump(previous | data, f)

def remove_from_db(discord_id: str):
	with open('db.json', 'r') as f:
		previous: dict = json.load(f)
	previous.pop(str(discord_id))
	with open('db.json', 'w') as f:
		json.dump(previous, f)