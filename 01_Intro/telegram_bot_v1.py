import telepot

if __name__ == '__main__':
	name = "Bot name"
	token = 'API token'
	TelegramBot = telepot.Bot(token)
	
	print (TelegramBot.getMe())
	#update_id = 0
	#print (TelegramBot.getUpdates(update_id+1))

