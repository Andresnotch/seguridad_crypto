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

if __name__ == '__main__':

	# Socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect to server
	address = 'localhost'
	port = 10000
	print(f'connecting to {address} port {port}')
	sock.connect((address, port))

	try:
		# Receive public key from server
		server_key = sock.recv(BUFFER)
		# Send public key to server
		sock.send(pkclient.encode())
		# Send public signing key
		public_sign_key = signing_key_client.verify_key.encode()
		sock.send(public_sign_key)
		print(f'Signing key: {public_sign_key}')
		# Create client box
		client_box = Box(skclient, PublicKey(server_key))

		with open('test', 'rb') as f:
			# Read whole file
			contents = f.read()
			# Encrypt whole file
			encrypted = client_box.encrypt(contents)
			# Send file info to allow server to know what to expect
			message = f'test {len(encrypted)}'.encode()
			print(f'sending {message}')
			sock.send(message)
			# Treat bytes as file (for ease of use)
			with io.BytesIO(encrypted) as b:
				remaining_bytes = len(encrypted)
				while remaining_bytes:
					read_bytes = b.read(BUFFER if BUFFER >= remaining_bytes else remaining_bytes)
					remaining_bytes -= len(read_bytes)
					print(read_bytes)
					if not read_bytes:
						# Break when finish reading
						break
					sock.sendall(read_bytes)
			signed_doc = signing_key_client.sign(encrypted)
			print(f'Signature: {signed_doc.signature}')
			print(f'Signed contents: {encrypted}')
			# Send signature
			sock.send(signed_doc.signature)
	except Exception:
		pass
	finally:
		print('closing socket')
		sock.close()