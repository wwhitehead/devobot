
import bot, config


@bot.Event()
def OnRequestTeleport(client, msg, sim):
	"""accept teleport requests from owner"""

	if msg.FromAgentName == config.owner:
		client.Self.TeleportLureRespond(msg.FromAgentID, True)

@bot.Event()
def OnObjectOffered(*args):
	"""accept any inventory offer"""
	
	return True
