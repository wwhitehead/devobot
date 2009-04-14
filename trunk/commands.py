

from command import Command


@Command()
def quit(client, msg):
	"""logout"""
	
	client.Network.Logout()
	

@Command(public=True)
def tp(client, msg):
	"""send the user a teleport request"""
	
	client.Self.SendTeleportLure(msg.FromAgentID)

