import os.path
import socket

BUFFER = 4096
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
        # Send file info to allow server to know what to expect
        message = f'test {file_size}'.encode()
        print(f'sending {message}')
        sock.send(message)

        with open('test', 'rb') as f:
            while True:
                read_bytes = f.read(BUFFER)
                if not read_bytes:
                    # Break when finish reading
                    break
                sock.sendall(read_bytes)
    except Exception:
        pass
    finally:
        print('closing socket')
        sock.close()