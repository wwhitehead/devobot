
import bot


@bot.Command(public=True)
def default(client, msg):
	"""default handler for instant messages"""

	print "%s: %s" % (msg.FromAgentName, msg.Message)

@bot.Command(public=True)
def tp(client, msg):
	"""send the user a teleport request"""
	
	client.Self.SendTeleportLure(msg.FromAgentID)

@bot.Command()
def quit(client, msg):
	"""logout"""
	
	client.Network.Logout()
