
import clr
clr.AddReferenceToFile("OpenMetaverse.dll")
clr.AddReferenceToFile("OpenMetaverseTypes.dll")
from OpenMetaverse import *
from OpenMetaverse.Packets import *
import config
from time import time, sleep


class _Events:
	"""wrapper class for all event handlers"""
	
	def handler(self, name):
		"""
		return a function tied to an event name that 
		looks up the set handler for the event
		"""
		
		def named_handler(*args):
			"""check for a set event handler and run it"""
			
			if hasattr(self, name):
				try:
					return getattr(self, name)(*args)
				except Exception, e:
					print "event error: %s" % e

		return named_handler


# create the event handler singleton and set the instant message event handler 
# to break each dialog type down into a seperate event
events = _Events()
events.OnInstantMessage = (lambda msg, sim: 
	events.handler("On%s" % msg.Dialog)(msg, sim))


def bound_client_handler_setting_appearance(client):
	"""
	returns a function with the client bound for updating appearance
	we need to have this as defining an inner function in login below
	causes a security exception with the exec calls used
	"""
	
	return lambda *args: client.Appearance.SetPreviousAppearance(False)
	

def login(credentials, sim=None, timeout=30):
	"""set up a client object and return it after logging in"""
	
	client = GridClient()
	client.Network.OnCurrentSimChanged += (
		client.Network.CurrentSimChangedCallback(
		bound_client_handler_setting_appearance(client)))
	
	# dynamically set the client settings from config
	for setting in config.settings.items():
		exec("client.%s = %s" % setting)

	# set up all the pre-defined events in config for 
	# later setting via the events wrapper
	for event in config.events:
		exec("client.%s += client.%sCallback(events.handler(\"%s\"))" % 
			(event, event.replace(".On", ".", 1), event.split(".", 1)[1]))
		
	# build the login variables
	args = list(credentials) + list(config.addr)
	if sim:
		args.insert(len(args) - 1, NetworkManager.StartLocation(*sim))

	# attempt login until success or timeout reached
	start = time()
	while time() - start < timeout:
		if client.Network.Login(*args):
			bound_client_handler_setting_appearance(client)()
			break
		sleep(.01)

	return client


def say(client, msg):
	"""shortcut for sending messages out to chat"""
	
	client.Self.Chat(str(msg), 0, ChatType.Normal)

	
class _Wait:
	"""handles waiting until an asynchronous event is completed"""
	
	def until(self, name, timeout=10):
		"""sleep until the event is set or the timeout is reached"""
		
		start = time()
		while not self.__dict__.get(name, False):
			if time() - start > timeout:
				return False
			sleep(.01)
		del self.__dict__[name]
		return True
		
	def __getattr__(self, name):
		"""return a function that will set the event as completed"""
		
		def setter(*args, **kwargs):
			self.__dict__[name] = True
			return True
		return setter
			
wait = _Wait()


#	added = []
#	for name in dir(client):
#		obj = getattr(client, name)
#		try:
#			for member in dir(obj):
#				try:
#					if "event" in str(type(getattr(obj, member))):
#						event = "%s.%s" % (name, member)
#						if event not in added:
#							exec("client.%s += client.%sCallback(events.handler(\"%s\"))" % 
#								(event, event.replace(".On", ".", 1), event.split(".", 1)[1]))
#							added.append(event)
#							print "added %s" % event
#				except Exception:
#					pass
#		except Exception:
#			pass
#	print "done"
