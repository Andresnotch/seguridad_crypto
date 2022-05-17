import socket
import nacl.utils
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from nacl.public import PrivateKey, Box, PublicKey
import nacl.pwhash
import db
import datetime as dt

BUFFER = 4096
skserver = PrivateKey.generate()
pkserver = skserver.public_key
database = db.DB()


class BankServer:

	def __init__(self):
		self.sock = self.__create_server__()
		self.logged_in = False
		self.current_client = None

	def __create_server__(self) -> socket:
		# Create socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind socket
		address = 'localhost'
		port = 10000
		print(f'starting up on {address} port {port}')
		sock.bind((address, port))

		# Listen for incoming connections
		sock.listen(1)
		return sock

	def receive_command(self):
		connection, client_address = self.sock.accept()
		try:
			print(f'connection from client {client_address[0]} at port {client_address[1]}')
			print('Creating secure connection...')
			# Send public key
			connection.send(pkserver.encode())
			# Receive public key from client
			client_key = connection.recv(BUFFER)
			# Receive public signing key from client
			client_verify_bytes = connection.recv(BUFFER)
			print(f'Signing key: {client_verify_bytes}')
			# Create VerifyKey obj
			verify_client = VerifyKey(client_verify_bytes)
			# Create server box
			server_box = Box(skserver, PublicKey(client_key))
			# receive command info from client (encrypted)
			size = connection.recv(BUFFER).decode()
			size = int(size)

			# Receive the data in small chunks
			command = b''
			while True:
				read_bytes = connection.recv(BUFFER if size >= BUFFER else size)
				size -= len(read_bytes)
				if not read_bytes:
					print(f'no data from client {client_address[0]} at port {client_address[1]}')
					break
				else:
					print(f'received {read_bytes}')
					command += read_bytes
			# Get signature
			client_signature = connection.recv(BUFFER)
			print('Signature: ' + str(client_signature))
			# Verify first
			verified = False
			try:
				verify_client.verify(command, client_signature)
				verified = True
			except Exception as e:
				print('This message was not sent by the client')
				print(e)

			if verified:
				# Decrypt after verification
				decrypted_command = server_box.decrypt(command).decode()
				print(decrypted_command)
				try:
					returnmessage = self.parse_command(decrypted_command)
				except Exception as e:
					returnmessage = e
				connection.send(f'{len(returnmessage.encode())}'.encode())
				connection.sendall(returnmessage.encode())

		except Exception as e:
			print(e)
		finally:
			# Clean up the connection
			connection.close()

	def parse_command(self, command: str):
		c_split = command.split()
		if c_split[0] == 'login':
			return self.auth_login(*c_split[1:])
		if c_split[0] == 'logout':
			return self.auth_logout()
		if c_split[0] == 'new':
			return self.new_client(*c_split[1:])
		if c_split[0] == 'deposit':
			return self.deposit(c_split[1], int(c_split[2]))
		if c_split[0] == 'transfer':
			return self.transfer_money(c_split[1], int(c_split[2]))
		return 'Invalid command'

	def start_server(self):
		while True:
			# Wait for a connection
			print('waiting...')
			self.receive_command()

	def auth_login(self, clientname: str, password: str):
		if clientname not in database.inner['clients']:
			raise KeyError('There is no such client')
		orig_hash = database.inner['clients'][clientname]['password_hash']
		correct = nacl.pwhash.verify(orig_hash.encode(), password.encode())
		database.inner['logs'][str(dt.datetime.now().timestamp())] = {
			'client': clientname,
			'success': correct
		}
		database.save_db()
		self.current_client = database.inner['clients'][clientname]
		self.current_client['name'] = clientname
		self.logged_in = correct
		return f'Logged in: {self.logged_in}'

	def auth_logout(self):
		if not self.logged_in:
			raise PermissionError('You are not logged in')
		self.current_client = None
		self.logged_in = False
		return f'Logged out'

	def new_client(self, name: str, mail: str, password: str):
		if name in database.inner['clients']:
			raise ValueError('This client already exists')
		database.inner['clients'][name] = {
			'mail': mail,
			'money': 0,
			'password_hash': nacl.pwhash.str(password.encode()).decode()
		}
		database.save_db()
		return 'Client created'

	def delete_client(self):
		if not self.logged_in:
			raise PermissionError('You are not logged in')
		if self.current_client['name'] not in database.inner['clients']:
			raise KeyError('The client does not exist')
		del database.inner['clients'][self.current_client['name']]
		database.save_db()
		return 'Client deleted'

	def change_client_data(self, name: str, newclient: dict):
		if not self.logged_in:
			raise PermissionError('You are not logged in')
		if name not in database.inner['clients']:
			raise KeyError('The client does not exist, create it first')
		database.inner['clients'][name] = newclient
		database.save_db()
		return 'Data changed'

	def transfer_money(self, destination: str, amount: float):
		if not self.logged_in:
			raise PermissionError('You are not logged in')
		if destination not in database.inner['clients']:
			raise KeyError('One of the clients does not exist')
		if database.inner['clients'][self.current_client['name']]['money'] < amount:
			raise ValueError("You don't have enough funds")
		database.inner['clients'][destination]['money'] += amount
		database.inner['clients'][self.current_client['name']]['money'] -= amount
		database.save_db()
		return 'Money transferred'

	def deposit(self, destination: str, amount: float):
		if not self.logged_in:
			raise PermissionError('You are not logged in')
		if destination not in database.inner['clients']:
			raise KeyError('The client does not exist')
		if amount <= 0:
			raise ValueError('You cannot deposit this amount')
		database.inner['clients'][destination]['money'] += amount
		database.save_db()
		return 'Deposit made'
