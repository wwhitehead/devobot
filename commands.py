
import System, bot


@bot.Command(public=True)
def default(client, msg, args):
	"""default handler for instant messages"""

	print "[%s] %s: %s" % (client.Self.Name, msg.FromAgentName, msg.Message)

@bot.Command(public=True)
def tp(client, msg, args):
	"""send the user a teleport request"""

	client.Self.SendTeleportLure(msg.FromAgentID)

@bot.Command()
def quit(client, msg, args):
	"""logout"""
	
	bot.logout(client)
	
@bot.Command(public=True)
def come(client, msg, args):
	"""walk to the sender"""
	
	pos = (bot.Vector3(client.Self.GlobalPosition) - 
		client.Self.SimPosition + msg.Position)
	client.Self.AutoPilotCancel()
	client.Self.AutoPilot(pos.X, pos.Y, client.Self.SimPosition.Z)

@bot.Command(public=True)
def sit(client, msg, args):
	"""ground sit"""
	
	client.Self.SitOnGround()

@bot.Command()
def stand(client, msg, args):
	"""stand"""
	
	client.Self.Stand()

@bot.Command(public=True)
def look(client, msg, args):
	"""turn towards sender"""
	
	client.Self.Movement.TurnToward(msg.Position)

@bot.Command()
def wear(client, msg, args):
	"""wear an inventory folder"""
	
	client.Appearance.WearOutfit(System.Array[str](args.split(",")), False)



