import cliente as cl

client = None


def main():
	global client
	command = input('> ').split()
	while command[0] != 'exit':
		client = cl.BankClient()
		client.send_command(' '.join(command))
		command = input('> ').split()
	client.exit()


# Logout

if __name__ == '__main__':
	main()
