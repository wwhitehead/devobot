

class Command:
	"""decorator for text command functions to flag them as commands and 
	specify their access level
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


class Event(Command):
	"""gives events a type that can be checked against"""
	pass
	
	
import clr
clr.AddReferenceToFile("OpenMetaverse.dll")
clr.AddReferenceToFile("OpenMetaverseTypes.dll")
from OpenMetaverse import *
from System.IO import FileSystemWatcher, Directory, IOException
from System.Threading import Thread
from System import DateTime
import config, commands, events as handlers


# owner's uuid
owner_id = None

# dict of client objects / bound event names stored for access in _reload
_client_bound_events = {}

# list of sl event stored for access in _reload
_sl_events = []


def _reload():
	"""reloads event handlers, config settings and commands and applies to 
	clients called when a file is modified, a client logs in or a command is 
	triggered
	"""
	
	# reload relevant modules
	map(reload, (handlers, config, commands))
	
	# build list of sl event names once
	global _sl_events
	if _client_bound_events and not _sl_events:
		client = _client_bound_events.keys()[0]
		for name in dir(client):
			obj = getattr(client, name)
			try:
				for member in dir(obj):
					try:
						if "event" in str(type(getattr(obj, member))).lower():
							event = "%s.%s" % (name, member)
							if event not in _sl_events:
								_sl_events.append(event)
					except:
						pass
			except:
				pass
	
	# bind settings and sl event handlers
	handlers.OnChat = None
	for client, bound in _client_bound_events.items():
		for setting in config.settings.items():
			exec("client.%s = %s" % setting)
		for event in _sl_events:
			name = event.split(".")[-1]
			if name in dir(handlers) and name not in bound:
				_client_bound_events[client].append(name)
				handler = events.handler(client, name)
				exec("client.%s += client.%sCallback(handler)" % 
					(event, event.replace(".On", ".", 1)))

	# set the relevant event handlers for commands
	handlers.OnMessageFromAgent = _command
	handlers.OnMessageFromObject = _command
	handlers.OnChat = _chat_command

	# bind the python event handlers
	for name in dir(handlers):
		handler = getattr(handlers, name)
		if isinstance(handler, handlers.bot.Event):
			setattr(events, name, handler)


@handlers.bot.Event()
def _chat_command(client, msg, audible, type, source, name, id, owner, pos):
	"""create an InstantMesage-like object from chat events and pass it to the 
	im handler
	"""
	
	class MessageWrapper:
		def __init__(self, **kwargs):
			self.__dict__.update(kwargs)

	if str(source) != "System" and "Typing" not in str(type):
		dialog = getattr(InstantMessageDialog, "MessageFrom%s" % source)
		msg = MessageWrapper(Message=msg, FromAgentName=name, FromAgentID=owner, 
			Position=pos, Dialog=dialog)
		_command(client, msg, client.Network.CurrentSim)
	
	
@handlers.bot.Event()
def _command(client, msg, sim):
	"""check instant message for valid command and execute"""
	
	command, args = ("%s " % msg.Message).lstrip("~").split(" ", 1)
	command = getattr(commands, command, getattr(commands, "default", None))
	if (isinstance(command, commands.bot.Command) and 
		msg.FromAgentID != client.Self.AgentID and 
		(msg.FromAgentID == owner_id or command.public)):
		try:
			command(client, msg, args.rstrip(" "))
		except Exception, e:
			print "command execute error: %s" % e


def login(credentials, sim=None, timeout=30):
	"""set up a client object and return it after logging in"""
	
	client = GridClient()

	# handler required for bot's avatar to render when changing sims
	client.Network.OnSimConnected += client.Network.SimConnectedCallback(
		lambda *args: client.Appearance.SetPreviousAppearance(False))
		
	# handler required for converting instant messages into Dialog events
	client.Self.OnInstantMessage += client.Self.InstantMessageCallback(
		lambda msg, sim: events.handler(client, "On%s" % msg.Dialog)(msg, sim))
			
	# add to client dict
	_client_bound_events[client] = ["OnInstantMessage"]

	# build the login variables
	args = list(credentials) + list(config.addr)
	if sim:
		args.insert(len(args) - 1, client.Network.StartLocation(*sim))
	
	# attempt login until success or timeout reached
	start = DateTime.Now
	while (DateTime.Now - start).Seconds < timeout:
		if client.Network.Login(*args):
			
			# find owner name and bind all
			@handlers.bot.Event()
			def owner_found(client, query, results):
				global owner_id
				for result in results:
					if "%s %s" % (result.FirstName, result.LastName) == config.owner:
						owner_id = UUID(result.AgentID)
						events.owner_found()
			handlers.OnDirPeopleReply = owner_found
			_reload()
			client.Directory.StartPeopleSearch(
				client.Directory.DirFindFlags.People, config.owner, 0)
			events.wait("owner_found", 30)
			handlers.OnDirPeopleReply = None
			break

		events.sleep(.01)

	return client


def logout(client):
	"""remove client from global objects dict on logout"""
	
	client.Network.Logout()
	del _client_bound_events[client]
	

def say(client, msg):
	"""shortcut for sending messages out to chat"""
	
	client.Self.Chat(str(msg), 0, ChatType.Normal)
	

def clients():
	"""helper that returns all clients"""
	
	return _client_bound_events.keys()


def command(client, command):
	"""external interface for running a command as the bot owner"""
	
	_chat_command._command(client, command, "", "", "Agent", config.owner, 
		owner_id, owner_id, client.Self.SimPosition)

class _Events:
	"""wrapper class for all event handlers and waiting"""
	
	def handler(self, client, name):
		"""return a function tied to a client and event name that looks up the 
		set handler for the event
		"""
		
		def named_handler(*args):
			"""check for a set event handler and run it"""
			
			args = list(args)
			args.insert(0, client)
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
			if (DateTime.Now - start).Seconds > timeout:
				return False
			Thread.CurrentThread.Join(.01)
		del self.__dict__[name]
		return True
		
	def sleep(self, time):
		"""wait for a non-existant event to timeout"""
		
		return self.wait(None, timeout=time)
		
	def __getattr__(self, name):
		"""return a function that will set the event as completed"""
		
		if name.startswith("On"):
			raise AttributeError
		def setter(*args, **kwargs):
			self.__dict__[name] = True
			return True
		return setter

events = _Events()


# set up directory watcher to automatically reload
def _watcher_reload(source, event):
	
	if event.Name in ("commands.py", "config.py", "events.py"):
		error = None
		try:
			_reload()
		except IOException:
			# file can still be held by write process and reload fails - retry
			_watcher_reload(source, event)
		except SyntaxError, e:
			if "The process cannot access the file" in str(e):
				_watcher_reload(source, event)
			else:
				error = e
		except Exception, e:
			error = e
		if error:
			print "reload error: %s" % error

_watcher = FileSystemWatcher()
_watcher.Path = Directory.GetCurrentDirectory()
_watcher.Changed += _watcher_reload
_watcher.EnableRaisingEvents = True


if __name__ == "__main__":
	for login_info in config.logins:
		login(*login_info)
	while True:
		msg = raw_input("> ")
		for client in clients():
			command(client, msg)

