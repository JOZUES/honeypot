# advanced_honeypot.py
import socket
import paramiko
import threading
import logging
import time

logging.basicConfig(level=logging.INFO, filename='honeypot.log', format='%(asctime)s - %(levelname)s - %(message)s')

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        client_address = self.get_transport().getpeername()[0]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        logging.info(f"Authentication attempt - Username: {username}, Password: {password}, From IP: {client_address}, Timestamp: {timestamp}")
        
        # Additional logging for IP address and timestamp
        logging.info(f"From IP: {client_address}, Timestamp: {timestamp}")

        # Implement further actions or alerts based on your requirements

        return paramiko.AUTH_FAILED

def start_honeypot():
    host = '127.0.0.1'  # Listen on all available interfaces
    port = 22  # SSH port

    while True:
        try:
            # Create a socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to a specific address and port
            server_socket.bind((host, port))

            # Listen for incoming connections
            server_socket.listen(5)

            print(f'Advanced Honeypot is listening on port {port}')

            # Accept a connection from a client
            client_socket, client_address = server_socket.accept()

            print(f'Connection from: {client_address}')

            # Create a new SSH server instance
            ssh_server = paramiko.Transport(client_socket)
            ssh_server.add_server_key(paramiko.RSAKey(filename='private_key.pem'))

            server = SSHServer()

            # Start the SSH server
            ssh_server.start_server(server=server)

            # Wait for the client to connect
            channel = ssh_server.accept(20)

            if channel is None:
                print('*** No channel.')
                client_socket.close()
                continue

            # Close the connection
            channel.close()
            client_socket.close()

        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {port} is already in use. Trying a different port.")
                port += 1
            else:
                raise

if __name__ == "__main__":
    start_honeypot()
