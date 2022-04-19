import socket
import sys

from Crypto.aleatorios import generate_random_string

if __name__ == '__main__':

    # Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    address = 'localhost'
    port = 10000
    print(f'connecting to {address} port {port}')
    sock.connect((address, port))

    try:

        # Send data
        message = bytes(generate_random_string(64), 'ascii')
        print(f'sending {message}')
        sock.sendall(message)

        # Look for the response
        received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(64)
            amount_received += len(data)
            print(f'received {data}')
    except Exception:
        pass
    finally:
        print('closing socket')
        sock.close()