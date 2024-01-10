from mojang import API
from hypixel import HypixelException
import os, uuid, hypixel, asyncio
from dotenv import load_dotenv

load_dotenv()
mojang = API()

def get_uuid(username: str) -> str:
	try:
		playerUUID = mojang.get_uuid(username)
	except:
		return None
	return str(uuid.UUID(playerUUID))

async def check_guild(uuid: str):
	client = hypixel.Client(os.getenv('HYPIXEL_API_KEY'))
	async with client:
		return await client.player(uuid)

def compare_usernames(dcUsername: str, hypixelUsername: str):
	dcUsername = dcUsername.removesuffix('#0')
	hypixelUsername = hypixelUsername.removesuffix('#0')
	if '#' in dcUsername and '#' in hypixelUsername:
		legacyUsername = True
	return dcUsername == hypixelUsername