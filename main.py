from mojang import API
from dotenv import load_dotenv
import os, discord
from discord.ext import commands
from discord import ui
from api import *

load_dotenv()

class VerificationBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix='=', intents=discord.Intents.all())
		self.synced = False

	async def setup_hook(self) -> None:
		self.add_view(VerifyButton())

	async def on_ready(self):
		await self.wait_until_ready()
		if not self.synced:
			#await self.tree.sync()
			self.synced = True
		await self.change_presence(activity=discord.Game(name='Bedwars'),status=discord.Status.online)
		await self.load_extension('jishaku')
		print(f"We have logged in as {self.user}.")
			
class VerifyButton(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Verify', style=discord.ButtonStyle.green, custom_id='verification:button', emoji='🔗')
	async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_modal(VerifyModal())
		

class VerifyModal(discord.ui.Modal):
	def __init__(self):
		super().__init__(title='Pikopian Empire Verification')
		
	username = ui.TextInput(
		label='Hypixel Username',
		style=discord.TextStyle.short,
		min_length=3,
		max_length=16
	)
	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		await interaction.followup.send('Verifying...')
		uuid = get_uuid(self.username)
		if uuid == None:
			await interaction.followup.send('❌ Invalid username!', ephemeral=True)
			return

client = VerificationBot()
mcAPI = API()

@client.tree.command(name='setup',description='Setup the verification system.')
async def setup(interaction: discord.Interaction):
	await interaction.response.defer()
	await interaction.followup.send('Setting up the verification system...', ephemeral=True)
	embed=discord.Embed(title="Hypixel Verification", description="Please verify yourself to get access to channels. In order to get verified, you will have to link your Discord username to your Hypixel account. Attached is a GIF that shows the process.", color=0x00ff00)
	embed.set_thumbnail(url="https://www.dropbox.com/scl/fi/7wsacdmogm3jmnnnm1mua/verifygif.gif?rlkey=7flriqaqvhzq5f5yryyo88aed&raw=1")
	embed.add_field(name="Is this a scam?", value="We will **never** ask you for your email, password, or any codes that Microsoft will send you. All we ask for is your **Minecraft Username** so we can check if you are in the guild or not.", inline=True)
	embed.add_field(name="Join the guild", value="Not yet a member of the guild? Apply now with `/guild join Pikopian Empire`", inline=True)
	embed.set_footer(text="Any issues? Contact sorkopiko")
	await interaction.channel.send(embed=embed, view=VerifyButton())

client.run(os.getenv("TOKEN"))