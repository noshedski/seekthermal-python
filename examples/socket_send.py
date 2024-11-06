import socket

def send_message(message, host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message.encode())
        data = s.recv(1024)
    print('Received', repr(data))

if __name__ == "__main__":
    send_message("New World")