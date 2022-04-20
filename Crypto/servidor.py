import socket

BUFFER = 4096

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
            # receive file info from client
            fname, fsize = connection.recv(BUFFER).decode().split(' ')
            fsize = int(fsize)

            # Receive the data in small chunks
            with open(f'{fname}_received', 'wb') as f:
                while True:
                    read_bytes = connection.recv(BUFFER)
                    if not read_bytes:
                        print(f'no data from client {client_address[0]} at port {client_address[1]}')
                        break
                    else:
                        print(f'received {read_bytes}')
                        f.write(read_bytes)
        except Exception:
            break
        finally:
            # Clean up the connection
            connection.close()