import bot, config

for login in config.logins:
	bot.login(login)
while True:
	msg = raw_input("> ")
	for client in bot.clients():
		bot.command(client, msg)

