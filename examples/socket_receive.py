import socket

def main():
    # Define the server address and port
    server_address = ('localhost', 65432)
    
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Bind the socket to the address and port
        sock.bind(server_address)
        
        # Listen for incoming connections
        sock.listen(1)
        print(f"Listening on {server_address}")
        
        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            with connection:
                print(f"Connected by {client_address}")
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    print(f"Received message: {data.decode('utf-8')}")
                    connection.sendall(data)

if __name__ == "__main__":
    main()