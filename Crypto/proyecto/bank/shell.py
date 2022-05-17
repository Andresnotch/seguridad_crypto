import servidor as sr

server = None

def main():
	global server
	command = input('> ')
	while command != 'exit':
		if command.split()[0] == 'start':
			server = sr.BankServer()
			server.start_server()
		command = input('> ')


if __name__ == '__main__':
	main()
