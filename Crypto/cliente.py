import io
import os.path
import socket
import nacl.utils
from nacl.public import PrivateKey, Box, PublicKey

BUFFER = 4096
skclient = PrivateKey.generate()
pkclient = skclient.public_key
file_size = os.path.getsize('test')

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
        # Create client box
        client_box = Box(skclient, PublicKey(server_key))
        # Send file info to allow server to know what to expect
        message = f'test {file_size}'.encode()
        print(f'sending {message}')
        sock.send(message)

        with open('test', 'rb') as f:
            # Read whole file
            contents = f.read()
            # Encrypt whole file
            encrypted = client_box.encrypt(contents)
            # Treat bytes as file (for ease of use)
            with io.BytesIO(encrypted) as b:
                while True:
                    read_bytes = b.read(BUFFER)
                    if not read_bytes:
                        # Break when finish reading
                        break
                    sock.sendall(read_bytes)
    except Exception:
        pass
    finally:
        print('closing socket')
        sock.close()