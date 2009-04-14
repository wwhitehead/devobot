
import bot, config, commands
from command import Command


def command(msg, sim):
	"""check instant message for valid command and execute"""
	
	char = "~"
	if msg.Message.startswith(char):
		command = msg.Message.lstrip(char).split(" ", 1)[0]
		
		# reload command definitions every time a command is called
		# this disregards performance for the sake of rapid development
		try:
			reload(commands)
		except Exception, e:
			bot.say(client, "command reload error: %s" % e)
		else:
			# check the command exists
			if command in dir(commands):
				command = eval("commands.%s" % command.lstrip(char))

		# ensure command is a command and it's either public or called by owner
		if isinstance(command, Command) and (command.public or
			msg.FromAgentName == config.owner):
			try:
				command(client, msg)
			except Exception, e:
				bot.say(client, "command execute error: %s" % e)


def teleport(msg, sim):
	"""accept teleport requests from owner"""
	
	if msg.FromAgentName == config.owner:
		client.Self.TeleportLureRespond(msg.FromAgentID, True)


# start
client = bot.login(config.login)
bot.events.OnRequestTeleport = teleport
bot.events.OnMessageFromAgent = command
bot.events.OnMessageFromObject = command
