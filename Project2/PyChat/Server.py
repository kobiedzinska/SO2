import socket
import threading
import sys

class ChatServer:

    # Initial server configuration
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None

        self.clients = [] # List to store active client connections
        self.running = True # Flag for server's status


    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # We create server socket, AF_INET = ipv4, SOCK_STREAM = TCP Connection
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)   # Enables reusability of address IP and port number after closing server
            self.server_socket.bind((self.host, self.port))                                 # assigning socket's address IP and port number to listen
            self.server_socket.listen(5)                                                    # we listen max 5 connections

            print(f"[SERVER] Started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"[SERVER] New connection from {client_address}")
                except Exception as e:
                    if self.running:
                        print(f"[SERVER] Error accepting connection: {e}")
                    break
        except Exception as e:
            print(f"[SERVER] Error starting server: {e}")
        finally:
            self.shutdown()


    def shutdown(self):
        self.running = False


    def handle_client(conn, addr):
        pass


if __name__ == "__main__":
    try:
        # Assigning values for ip address and port number
        host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

        # Create and start the server
        server = ChatServer(host, port)
        server.start()

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down server...")
    except Exception as e:
        print(f"[SERVER] Error: {e}")