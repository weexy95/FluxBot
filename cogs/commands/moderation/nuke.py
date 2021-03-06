import discord
import hex_colors
import asyncio

from discord.ext import commands


class Nuke(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(
		name='nuke',
		help='Delete a channel and make a copy of it',
		usage='[channel]',
		aliases=["resetchannel", 'selfdestruct'],
		description="Use this command to delete a channel and then make a new copy of it, basically making it look like everything was deleted... Also note that this command will delete all the messages including pinned messages"
	)
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(administrator=True)
	async def nuke(self, ctx, channel: discord.TextChannel = None):
		if channel is None:
			channel = ctx.channel

		async def view_timeout():
			timeup_embed = discord.Embed(
				title="Time up!!",
				description="The nuke was cancelled because you were too late to respond.."
			)
			await choices.edit(embed=timeup_embed, view=None)
			await choices.delete(delay=5)
			return

		async def cancel_click(interaction):
			if interaction.user.guild_permissions.administrator:
				await interaction.message.edit(embed=discord.Embed(description=f"Cancelled the nuke, on behalf of {interaction.user.mention}", colour=hex_colors.l_green), view=None)
				await choices.delete(delay=5)
				view.stop()
				return
			else:
				pass

		async def ok_click(interaction):
			if interaction.user == ctx.author:
				try:
					new_channel = await channel.clone(
						reason=f'Original was nuked by {ctx.author}')  # Reason to be registered in the audit log
					await new_channel.edit(position=channel.position)
					await channel.delete()
					view.stop()
					interaction.message.edit(view=None)
				except discord.Forbidden:
					await ctx.send(
						"I couldn't delete the channel, maybe this is a community updates channel?")  # Channels that are set for community updates cannot be deleted without transferring the community updates to another channel
					await new_channel.delete()  # The clone is useless if the original still exists
			else:
				pass


			em = discord.Embed(
				title='This channel got nuked!',
				description='Who did this? Check Audit Log',
				color=hex_colors.m_red)

			await new_channel.send(embed=em)

		view = discord.ui.View(timeout=15)
		ok_butt = discord.ui.Button(label="Nuke!", style=discord.ButtonStyle.green)
		ok_butt.callback = ok_click
		view.add_item(ok_butt)
		cancel_butt = discord.ui.Button(label="Cancel!", style=discord.ButtonStyle.danger)
		cancel_butt.callback = cancel_click
		view.add_item(cancel_butt)
		view.on_timeout = view_timeout

		confirmation = discord.Embed(
			description=f"Are you sure you want to nuke <#{ctx.channel.id}>?",
			color=0xF59E42
		)
		choices = await ctx.send(embed=confirmation, view=view)


def setup(client):
	client.add_cog(Nuke(client))
