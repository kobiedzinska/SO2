import socket
import threading
import sys
import queue

class ChatServer:

    # Initial server configuration
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None

        self.clients = []   # List to store active client connections
        self.running = True # Flag for server's status

        # We're locking shared resources
        self.clients_lock = threading.Lock()
        self.console_lock = threading.Lock()
        # Message queue and  semaphore
        self.message_queue = queue.Queue()


    def start(self):
        try:
            print("[SERVER] Creating server...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # We create server socket, AF_INET = ipv4, SOCK_STREAM = TCP Connection
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)   # Enables reusability of address IP and port number after closing server
            self.server_socket.bind((self.host, self.port))                                 # assigning socket's address IP and port number to listen
            self.server_socket.listen(5)                                                    # we listen max 5 connections

            with self.console_lock:
                print(f"[SERVER] Started on {self.host}:{self.port}")

            # Creating message dispatcher thread
            message_dispatcher = threading.Thread(target=self.dispatch_messages)
            message_dispatcher.daemon = True
            message_dispatcher.start()


            ## Accepting CLIENT connections
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    with self.console_lock:
                        print(f"[SERVER] New connection from {client_address}")



                except Exception as e:
                    if self.running:
                        with self.console_lock:
                            print(f"[SERVER] Error accepting connection: {e}")
                    break

        except Exception as e:
            with self.console_lock:
                print(f"[SERVER] Error starting server: {e}")
        finally:
            self.shutdown()


    def shutdown(self):
        self.running = False

    def handle_client(self, client_socket, client_address):
        client_id = f"CLient-{client_address[0]}:{client_address[1]}"

        try:
            with self.clients_lock:
                self.clients.append((client_id,client_id))

            welcome_message = f"Welcome {client_id}! There are {len(self.clients)} client(s) connected."
            client_socket.send(welcome_message.encode('utf-8'))

            self.queue_message(f"[SERVER] {client_id} has joined the chat.")

            # CLIENT is sending messages
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    message = data.decode('utf-8').strip()

                    if message.lower() == 'exit':
                        break

                    formatted_message = f"{client_id}: {message}"
                    self.queue_message(formatted_message)

                except ConnectionResetError:
                    break
                except Exception as e:
                    with self.console_lock:
                        print(f"[SERVER] Error receiving from {client_id}: {e}")
                    break

        ### CLIENT is leaving server
        finally:
            # Removing client from client list
            with self.clients_lock:
                self.clients = [c for c in self.clients if c[0] != client_socket]

            # Broadcasting message that client has left the chat
            self.queue_message(f"[SERVER] {client_id} has left the chat.")

            # Closing socket
            try:
                client_socket.close()
            except:
                pass

            # We inform server that client has left
            with self.console_lock:
                print(f"[SERVER] Connection with {client_id} closed")


    def queue_message(self, message):
        self.message_queue.put(message)

## Dispatching messages to all clients
    def dispatch_messages(self):
        while self.running:
            try:
                # if there will be 1s timeout
                try:
                    message = self.message_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # we protect the console, so many threads wouldn't print messages simultaneously
                with self.console_lock:
                    print(f"[BROADCAST] {message}")

                # copy of shared list - critical section
                with self.clients_lock:
                    current_clients = self.clients.copy()

                for client_socket, _ in current_clients:
                    try:
                        client_socket.send(f"{message}\n".encode('utf-8'))
                    except:
                        pass

                # Mark the processed message
                self.message_queue.task_done()

            except Exception as e:
                with self.console_lock:
                    print(f"[SERVER] Error in dispatch_messages function: {e}")

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