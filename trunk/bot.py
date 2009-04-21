
import clr
clr.AddReferenceToFile("OpenMetaverse.dll")
clr.AddReferenceToFile("OpenMetaverseTypes.dll")
from OpenMetaverse import *
from System.IO import FileSystemWatcher, Directory
from System.Threading import Thread
from System import DateTime
import config, commands, events as handlers


# list of client objects - stored for access in _bind_all
_clients = []


def _bind_all():
	"""
	reloads event handlers, config settings and commands and applies to clients
	called when a file is modified, a client logs in or a command is triggered
	"""
	
	# reload relevant modules
	map(reload, (handlers, config, command))
	
	for client in clients:

		# bind settings
		for setting in config.settings.items():
			exec("client.%s = %s" % setting)
		
		# bind event handlers
		for event in config.events:
			name = event.split(".")[-1]
			if name in dir(handlers) and name not in ("OnInstantMessage", 
				"OnMessageFromAgent", "OnMessageFromObject"):
				if not hasattr(events, name):
					exec("client.%s += client.%sCallback(events.handler(client," +
						"\"%s\"))" % (event, event.replace(".On", ".", 1), name))
				setattr(events, name) = getattr(handlers, name)
	

def _command(msg, sim):
	"""check instant message for valid command and execute"""
	
	char = "~"
	if msg.Message.startswith(char):
		command = msg.Message.lstrip(char).split(" ", 1)[0]
		
		# bind all every time a command is called
		try:
			_bind_all()
		except Exception, e:
			print "bot.bind_all error: %s" % e
		else:
			# check the command exists
			if command not in dir(commands) and "default" in dir(commands):
				command = "default"
			if command in dir(commands):
				command = getattr(commands, command.lstrip(char))

		# ensure command is a command and it's either public or called by owner
		if isinstance(command, Command) and (command.public or
			msg.FromAgentName == config.owner):
			try:
				command(client, msg)
			except Exception, e:
				print "command execute error: %s" % e
				

def login(credentials, sim=None, timeout=30):
	"""set up a client object and return it after logging in"""
	
	client = GridClient()

	# handler required for bot's avatar to render when changing sims
	appearance = lambda *args: client.Appearance.SetPreviousAppearance(False)
	client.Network.OnCurrentSimChanged += (
		client.Network.CurrentSimChangedCallback(appearance))

	# handler required for converting instant messages into Dialog events
	client.Self.OnInstantMessage += (client.Self.InstantMessageCallback(
		lambda msg, sim: events.handler("On%s" % msg.Dialog)(msg, sim)))
			
	# add to clients list and bind all
	_clients.append(client)
	_bind_all()

	# build the login variables
	args = list(credentials) + list(config.addr)
	if sim:
		args.insert(len(args) - 1, NetworkManager.StartLocation(*sim))
	
	# attempt login until success or timeout reached
	start = DateTime.Now
	while (DateTime.Now - start).Seconds < timeout:
		if client.Network.Login(*args):
			appearance()
			break
		Thread.Sleep(.01)

	return client


def say(client, msg):
	"""shortcut for sending messages out to chat"""
	
	client.Self.Chat(str(msg), 0, ChatType.Normal)


class Command:
	"""
	decorator for text command functions to flag them as commands 
	and specify their access level
	"""
	
	def __init__(self, public=False):
		"""set access level"""
		
		self.public = public
		
	def __call__(self, *args):
		"""bind command on first call"""

		if not hasattr(self, "_command"):
			self._command = args[0]
			return self
		else:
			return self._command(*args)


class _Events:
	"""wrapper class for all event handlers and waiting"""
	
	def handler(self, client, name):
		"""
		return a function tied to a client and event name that 
		looks up the set handler for the event
		"""
		
		def named_handler(*args):
			"""check for a set event handler and run it"""
			
			args = list(args)
			args.insert(client)
			if hasattr(self, name):
				try:
					return getattr(self, name)(*args)
				except Exception, e:
					print "event error: %s" % e

		return named_handler

	def wait(self, name, timeout=10):
		"""sleep until the event is set or the timeout is reached"""
		
		start = DateTime.Now
		while not self.__dict__.get(name, False):
			if (DateTime.Now - start).Seconds > timeout
				return False
			Thread.Sleep(.01)
		del self.__dict__[name]
		return True
		
	def __getattr__(self, name):
		"""return a function that will set the event as completed"""
		
		def setter(*args, **kwargs):
			self.__dict__[name] = True
			return True
		return setter


# set up events 
events = _Events()
events.OnMessageFromAgent = _command
events.OnMessageFromObject = _command

# set up directoy watcher to automatically reload via bind_all
def _watcher_bind_all(source, event)
	if event.FullPath.lower.endswith(".py"):
		_bind_all()

_watcher = FileSystemWatcher()
_watcher.Path = Directory.GetCurrentDirectory()
_watcher.Changed += _bind_all
_watcher.EnableRaisingEvents = True


if __name__ == "__main__":
	login(config.login)