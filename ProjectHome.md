[DevoBot](http://code.google.com/p/devobot/) provides a base framework for writing [SecondLife](http://secondlife.com/) bots that are controlled via commands sent through instant messages. The main goal is to allow extremely rapid development by providing the ability to modify source code without having to recompile or even relog the bot account.

### Support ###

If you have a legitimate bug or patch then by all means use the issue tracker but otherwise please do not request assistance here for issues specific to libomv or for [IronPython](http://www.codeplex.com/IronPython) help as there's already a wealth of information available for these online. Here are some starting points:

  * [libomv](http://lib.openmetaverse.org/)
  * [ironpython.info](http://ironpython.info/)

### Installation ###

Note: Mono users will require at least [mono 2.4.x](http://ftp.novell.com/pub/mono/sources-stable/)

  1. Check out the [source code](http://code.google.com/p/devobot/source/checkout)
  1. Rename `config.py.example` to `config.py`
  1. Edit `config.py` and set the `owner` and `login` variables
  1. Run `run.py` with [IronPython](http://www.codeplex.com/IronPython)

### Adding Commands ###

Simply add function definitions inside `commands.py` - these functions only have two requirements. Firstly they must be prefixed with the `@bot.Command` decorator and secondly they must have two required arguments, `client` and `msg` eg:

```
@bot.Command()
def my_command(client, msg):
    # do something
```

The `@bot.Command` decorator simply identifies the function as a command. This allows you to have other functions and variables inside `commands.py` that aren't accessible as commands. By default a command is only available to the owner specified in `config.py` - to make a command publicly accessible add the `public` keyword argument to the `@bot.Command` decorator, eg:


```
@bot.Command(public=True)
def my_command(client, msg):
    # do something
```

The types for the two required arguments for a command function are respectively the `OpenMetaverse.GridClient` object that represents the current bot and the `OpenMetaverse.InstantMessage` object that represents the instant message used to trigger the command.

To trigger a command simply send the bot an instant message with the command name, prefixed with "~", so in order to trigger the quit command you'd send an instant message saying `~quit`

### Adding Events ###

There are two ways to specify event handlers. The first is similar to the approach for adding commands whereby event handlers are simply defined inside `events.py` as functions. To define an event handler simply name the function the same as its event in `OpenMetaverse`, providing the same list of parameters for the relevant event handler in `OpenMetaverse` along with an extra initial parameter representing the `OpenMetaverse.GridClient` object. You must also use the `@bot.Event` decorator to identify the function as an event handler, eg:

```
@bot.Event()
def OnChat(client, msg, audible, type, source, name, id, owner, pos):
    """print chat"""
	
    print "[%s/chat] %s: %s" % (client.Self.Name, name, msg)
```

The second way for defining event handlers is to explicitly assign them inside your own code.
To assist in applying many modifications to a bot while it is still logged in, a method is provided for specifically setting a master event handler for each event rather than having to deal with adding and removing multiple event handlers per event. To set a master event handler for a particular event, simply set the handler on `bot.events` eg:

```
import bot

# define a command that creates and sets a master event handler
@bot.Command()
def set_chat_handler(client, msg):

    def print_chat(client, msg, lvl, type, src_type, from_name, id, owner_id, pos):
	"""print chat"""

        print "[%s/chat] %s: %s" % (client.Self.Name, name, msg)

    bot.events.OnChat = print_chat
```

Note that you must still provide the extra initial parameter representing the `OpenMetaverse.GridClient` object however in this case it's unnecessary to use the `@bot.Event` decorator since you're explicitly defining the event handler.

The key idea here is that you can modify and run the `print_chat` function over and over as many times as you like and the `OnChat` event will only ever be triggered once each time.

You can still add event handlers in the traditional way libopenmv intends you to however you may find less than desirable results by doing so with a bot that can be modified while it's running.

### OnInstantMessage ###

The `OnInstantMessage` event is treated specially and unavailable for use within the approaches described above for event handlers. This is not due to the handling of commands as described above but due to the large number of concerns that seem to pass through it. Basically the `OnInstantMessage` event is broken down into a separate event for each type of `InstantMessageDialog` so using the approaches described above for event handlers you can add specific handlers for things like `OnGroupInvitation` and `OnInventoryOffered`. If you need to handle instant messages that aren't valid commands, simply define a command called `default` inside `commands.py` which will be called when an instant message is received and a command is not triggered.

### Scripting Bots ###

Viewing the source of `run.py` shows that it simply performs an import of the bot module,  performs a login on all the credentials provided in `config.py` and then listens for commands typed in the console. This provides a starting point for scripting your own bots.