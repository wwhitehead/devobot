
import bot, config


@bot.Event()
def OnRequestTeleport(client, msg, sim):
	"""accept teleport requests from owner"""

	if msg.FromAgentName == config.owner:
		client.Self.TeleportLureRespond(msg.FromAgentID, True)


@bot.Event()
def OnChat(client, msg, audible, type, source, name, id, owner, pos):
	"""print chat"""
	
	if "Typing" not in str(type):
		print "[%s/chat] %s: %s" % (client.Self.Name, name, msg)

