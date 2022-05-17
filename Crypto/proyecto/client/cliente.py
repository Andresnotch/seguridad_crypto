import io
import os.path
import socket
import nacl.utils
from nacl.signing import SigningKey
from nacl.public import PrivateKey, Box, PublicKey

BUFFER = 4096
skclient = PrivateKey.generate()
pkclient = skclient.public_key
signing_key_client = SigningKey.generate()


class BankClient:

	def __init__(self):
		self.sock = self.__connect__()

	def __connect__(self) -> socket:
		# Socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to server
		address = 'localhost'
		port = 10000
		print(f'connecting to {address} port {port}')
		sock.connect((address, port))
		return sock

	def send_command(self, command: str):
		try:
			# Receive public key from server
			server_key = self.sock.recv(BUFFER)
			# Send public key to server
			self.sock.send(pkclient.encode())
			# Send public signing key
			public_sign_key = signing_key_client.verify_key.encode()
			self.sock.send(public_sign_key)
			print(f'Signing key: {public_sign_key}')
			# Create client box
			client_box = Box(skclient, PublicKey(server_key))

			# Encode command
			contents = command.encode()
			# Encrypt command
			encrypted = client_box.encrypt(contents)
			# Send command info to allow server to know what to expect
			message = f'{len(encrypted)}'.encode()
			print(f'sending {message}')
			self.sock.send(message)
			# Treat bytes as file (for ease of use)
			with io.BytesIO(encrypted) as b:
				remaining_bytes = len(encrypted)
				while remaining_bytes:
					read_bytes = b.read(BUFFER if BUFFER >= remaining_bytes else remaining_bytes)
					remaining_bytes -= len(read_bytes)
					print(f'Sending file: {read_bytes}')
					if not read_bytes:
						# Break when finish reading
						break
					self.sock.sendall(read_bytes)
			signed_doc = signing_key_client.sign(encrypted)
			print(f'Signature: {signed_doc.signature}')
			# Send signature
			self.sock.send(signed_doc.signature)

			size = self.sock.recv(BUFFER).decode()
			size = int(size)

			# Receive the data in small chunks
			returnmessage = b''
			while True:
				read_bytes = self.sock.recv(BUFFER if size >= BUFFER else size)
				size -= len(read_bytes)
				if not read_bytes:
					break
				else:
					print(f'received {read_bytes}')
					returnmessage += read_bytes

			print(returnmessage.decode())
		except Exception as e:
			print(e)
			return

	def exit(self):
		self.sock.close()

	def verify_file(self):
		try:
			# Receive public key from server
			server_key = self.sock.recv(BUFFER)
			# Send public key to server
			self.sock.send(pkclient.encode())
			# Send public signing key
			public_sign_key = signing_key_client.verify_key.encode()
			self.sock.send(public_sign_key)
			print(f'Signing key: {public_sign_key}')
			# Create client box
			client_box = Box(skclient, PublicKey(server_key))

			with open('../../test', 'rb') as f:
				# Read whole file
				contents = f.read()
				# Encrypt whole file
				encrypted = client_box.encrypt(contents)
				# Send file info to allow server to know what to expect
				message = f'test {len(encrypted)}'.encode()
				print(f'sending {message}')
				self.sock.send(message)
				# Treat bytes as file (for ease of use)
				with io.BytesIO(encrypted) as b:
					remaining_bytes = len(encrypted)
					while remaining_bytes:
						read_bytes = b.read(BUFFER if BUFFER >= remaining_bytes else remaining_bytes)
						remaining_bytes -= len(read_bytes)
						print(f'Sending file: {read_bytes}')
						if not read_bytes:
							# Break when finish reading
							break
						self.sock.sendall(read_bytes)
				signed_doc = signing_key_client.sign(encrypted)
				print(f'Signature: {signed_doc.signature}')
				# Send signature
				self.sock.send(signed_doc.signature)
		except Exception:
			return
		finally:
			print('closing socket')
			self.sock.close()
