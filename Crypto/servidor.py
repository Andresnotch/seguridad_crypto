import socket
import sys
if __name__ == '__main__':
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Binnd socket
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

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(64)
                if data:
                    print(f'received {data}')
                else:
                    print(f'no data from client {client_address[0]} at port {client_address[1]}')
                    break
        except Exception:
            break
        finally:
            # Clean up the connection
            connection.close()