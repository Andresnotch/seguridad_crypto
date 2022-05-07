import socket
import nacl.utils
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from nacl.public import PrivateKey, Box, PublicKey

BUFFER = 4096
skserver = PrivateKey.generate()
pkserver = skserver.public_key

if __name__ == '__main__':
	# Create socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind socket
	address = 'localhost'
	port = 10000
	print(f'starting up on {address} port {port}')
	sock.bind((address, port))

	# Listen for incoming connections
	sock.listen(1)

	while True:
		# Wait for a connection
		print('waiting...')
		connection, client_address = sock.accept()
		try:
			print(f'connection from client {client_address[0]} at port {client_address[1]}')
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
			# receive file info from client (encrypted)
			fname, fsize = connection.recv(BUFFER).decode().split(' ')
			fsize = int(fsize)

			# Receive the data in small chunks
			with open(f'{fname}_received', 'wb') as f:
				while True:
					read_bytes = connection.recv(BUFFER if fsize >= BUFFER else fsize)
					fsize -= len(read_bytes)
					if not read_bytes:
						print(f'no data from client {client_address[0]} at port {client_address[1]}')
						break
					else:
						print(f'received {read_bytes}')
						f.write(read_bytes)
			# Decrypt file
			with open(f'{fname}_received', 'rb') as f:
				contents = f.read()
				client_signature = connection.recv(BUFFER)
				print('Signature: ' + str(client_signature))
				# Verify first
				verified = False
				try:
					verify_client.verify(contents, client_signature)
					verified = True
				except Exception as e:
					print('This message was not sent by the client')
					print(e)

				if verified:
					# Decrypt after verification
					print(server_box.decrypt(contents).decode('utf-8'))
		except Exception:
			break
		finally:
			# Clean up the connection
			connection.close()