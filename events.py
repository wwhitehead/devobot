
import bot, config


def OnRequestTeleport(client, msg, sim):
	"""accept teleport requests from owner"""
	
	if msg.FromAgentName == config.owner:
		client.Self.TeleportLureRespond(msg.FromAgentID, True)