from mojang import API
from dotenv import load_dotenv
import os, discord, uuid, json
from discord.ext import commands, tasks
from discord import ui
from api import *
import json

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
		await updateLoop.start()
			
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
		self.username = str(self.username.value)
		await interaction.response.defer()

		msg = await interaction.followup.send('🔄 Verifying Username... [1/4]', ephemeral=True, wait=True)
		playerUUID = get_uuid(self.username)
		if playerUUID == None:
			await msg.edit(content='❌ Invalid username!')
			return
		elif playerUUID == False:
			await msg.edit(content='❌ Error [1/4]. Contact <@!609544328737456149>')
			return
		
		await msg.edit(content='🔄 Verifying Hypixel Account... [2/4]')
		stats = await check_stats(playerUUID)
		if stats == None:
			await msg.edit(content='❌ You have never joined Hypixel!')
			return
		elif stats == False:
			await msg.edit(content='❌ Error [2/4]. Contact <@!609544328737456149>')
			return
		
		await msg.edit(content='🔄 Verifying Discord Account... [3/4]')
		if stats.socials.discord == None:
			await msg.edit(content='❌ You have not linked your Discord account! Please follow the provided GIF to link it.')
			return
		dc = compare_usernames(interaction.user.name, stats.socials.discord)
		if dc == False:
			await msg.edit(content=f'❌ Incorrect Discord Account linked: `{stats.socials.discord}`. Your Discord username is `{interaction.user.name}`. Please follow the provided GIF to link it.')
			return
		elif stats == None:
			await msg.edit(content='❌ Error [3/4]. Contact <@!609544328737456149>')
			return

		await msg.edit(content='🔄 Verifying Guild... [4/4]')
		guild = await check_guild(self.username)
		if guild == None:
			await msg.edit(content='❌ You are not in a guild!')
			return
		elif guild.id != '659785438ea8c9dca6f379c5':
			await msg.edit(content='❌ You are not in the Pikopian Empire guild!')
			return
		elif guild == False:
			await msg.edit(content='❌ Error [4/4]. Contact <@!609544328737456149>')
			return
		
		member = next((
				member for member in guild.members if member.uuid == uuid.UUID(playerUUID).hex
			), None)
		with open('settings.json') as f:
			settings = json.load(f)
		
		await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=settings['member']))
		if member.rank.name in settings['ranks']:
			await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=settings['ranks'][member.rank.name]))

		await interaction.user.edit(nick=f'[{stats.bedwars.level}✫] {stats.name}')
		write_to_db(interaction.user.id, playerUUID)
		await msg.edit(content=f'✅ Verified as `[{stats.bedwars.level}✫] {stats.name}`!')

client = VerificationBot()
mcAPI = API()

@client.tree.command(name='setup',description='Setup the verification system.')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
	await interaction.response.send_message('Setting up the verification system...', ephemeral=True)
	embed=discord.Embed(title="Hypixel Verification", description="Please verify yourself to get access to channels. In order to get verified, you will have to link your Discord username to your Hypixel account. Attached is a GIF that shows the process.", color=0x00ff00)
	embed.set_thumbnail(url="https://www.dropbox.com/scl/fi/7wsacdmogm3jmnnnm1mua/verifygif.gif?rlkey=7flriqaqvhzq5f5yryyo88aed&raw=1")
	embed.add_field(name="Is this a scam?", value="We will **never** ask you for your email, password, or any codes that Microsoft will send you. All we ask for is your **Minecraft Username** so we can check if you are in the guild or not.", inline=True)
	embed.add_field(name="Join the guild", value="Not yet a member of the guild? Apply now with `/guild join Pikopian Empire`", inline=True)
	embed.set_footer(text="Any issues? Contact sorkopiko")
	await interaction.channel.send(embed=embed, view=VerifyButton())

@tasks.loop(minutes=5)
async def updateLoop():
	with open('settings.json') as f:
		settings = json.load(f)
	with open('db.json') as f:
		db = json.load(f)
	dcGuild = client.get_guild(settings["dcGuild"])
	memberRole = discord.utils.get(dcGuild.roles, id=settings['member'])
	guild = await id_guild(settings['guild'])
	everyone = discord.utils.get(dcGuild.roles, id=settings['everyone'])
	for user, mcUUID in db.items():
		dcMember = dcGuild.get_member(int(user))
		if dcMember == None:
			remove_from_db(user)
			continue
		member = next((
				member for member in guild.members if member.uuid == uuid.UUID(mcUUID).hex
			), None)
		if member == None:
			dcMemberRoles = dcMember.roles
			dcMemberRoles.remove(everyone)
			await dcMember.remove_roles(*dcMemberRoles)
			await dcMember.edit(nick=None)
			remove_from_db(user)
			continue
		await dcMember.add_roles(memberRole)
		if member.rank.name in settings['ranks']:
			newRole = discord.utils.get(dcGuild.roles, id=settings['ranks'][member.rank.name])
			await dcMember.add_roles(newRole)
			dcMemberRoles = dcMember.roles
			dcMemberRoles.remove(memberRole)
			dcMemberRoles.remove(newRole)
			dcMemberRoles.remove(everyone)
			if len(dcMemberRoles) > 0:
				await dcMember.remove_roles(*dcMemberRoles)
		else:
			dcMemberRoles = dcMember.roles
			dcMemberRoles.remove(memberRole)
			dcMemberRoles.remove(everyone)
			if len(dcMemberRoles) > 0:
				await dcMember.remove_roles(*dcMemberRoles)

		memberStats = await check_stats(mcUUID)
		await dcMember.edit(nick=f'[{memberStats.bedwars.level}✫] {memberStats.name}')
	print('Updated!')

client.run(os.getenv("TOKEN"))