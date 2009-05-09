
import bot


@bot.Command(public=True)
def default(client, msg):
	"""default handler for instant messages"""

	print "[%s] %s: %s" % (client.Self.Name, msg.FromAgentName, msg.Message)

@bot.Command(public=True)
def tp(client, msg):
	"""send the user a teleport request"""

	client.Self.SendTeleportLure(msg.FromAgentID)

@bot.Command()
def quit(client, msg):
	"""logout"""
	
	client.Network.Logout()
	
@bot.Command()
def come(client, msg):
	"""walk to the sender"""
	
	pos = (bot.Vector3(client.Self.GlobalPosition) - 
		client.Self.SimPosition + msg.Position)
	client.Self.AutoPilotCancel()
	client.Self.AutoPilot(pos.X, pos.Y, client.Self.SimPosition.Z)
