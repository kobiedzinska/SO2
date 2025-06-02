import socket
import threading
import sys
import queue

class ChatServer:

    # Initial server configuration
    def __init__(self, host, port):
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
        self.max_connections = 5
        self.connection_semaphore = threading.Semaphore(self.max_connections)

    def start(self):
        try:
            print("[SERVER] Creating server...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)

            with self.console_lock:
                print(f"[SERVER] Started on {self.host}:{self.port}")

            # Creating message dispatcher thread
            message_dispatcher = threading.Thread(target=self.dispatch_messages)
            message_dispatcher.daemon = True
            message_dispatcher.start()

            ## Accepting CLIENT connections
            while self.running:
                try:
                    # We're checking if there's space for connection
                    if self.connection_semaphore.acquire(blocking=False):
                        try:
                            client_socket, client_address = self.server_socket.accept()
                            with self.console_lock:
                                print(f"[SERVER] New connection from {client_address}")

                            # Creating client handling threads
                            client_thread = threading.Thread(
                                target=self.handle_client_with_semaphore,
                                args=(client_socket, client_address)
                            )
                            client_thread.daemon = True
                            client_thread.start()

                        except Exception as e:
                            # if there is an error with the semaphore
                            self.connection_semaphore.release()
                            if self.running:
                                with self.console_lock:
                                    print(f"[SERVER] Error accepting connection: {e}")
                            break
                    else:
                        # There's no free space for connection, we wait
                        with self.console_lock:
                            print("[SERVER] Max connections reached, waiting...")
                        threading.Event().wait(5.0)  # wait

                except Exception as e:
                    if self.running:
                        with self.console_lock:
                            print(f"[SERVER] Error in main loop: {e}")
                    break

        except Exception as e:
            with self.console_lock:
                print(f"[SERVER] Error starting server: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        self.running = False

        # We're closing clients sockets
        with self.clients_lock:
            for client_socket, _ in self.clients:
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear() # we're clearing the clients list

        # We're closing server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        with self.console_lock:
            print("[SERVER] Server shutdown complete")

    def handle_client_with_semaphore(self, client_socket, client_address):
        try:
            self.handle_client(client_socket, client_address)
        finally:
            # Always release the semaphore when client handling is done
            self.connection_semaphore.release()

    def handle_client(self, client_socket, client_address):
        client_id = f"Client-{client_address[0]}:{client_address[1]}"

        try:
            with self.clients_lock:
                self.clients.append((client_id, client_socket)) # We add client to the shared list of clients on the chat

            welcome_message = f"Welcome {client_id}!"
            client_socket.send(welcome_message.encode('utf-8'))

            self.queue_message(f"[SERVER] {client_id} has joined the chat.")

            # CLIENT is sending messages
            while self.running:
                try:
                    data = client_socket.recv(1024) # We receive 1024 bytes/chars from client
                    if not data:    # if the client has left the chat we stop the thread
                        break

                    message = data.decode('utf-8').strip() # We decode the message from bytes to readible text

                    if message.lower() == '/exit':  # if client has written '/exit' we remove the client from server
                        break

                    # We send messages from client with the special formatting
                    formatted_message = f"{client_id}: {message}"
                    self.queue_message(formatted_message)

                except ConnectionResetError:
                    break
                except Exception as e:
                    with self.console_lock:
                        print(f"[SERVER] Error receiving from {client_id}: {e}")
                    break

        ### CLIENT is being removed from server
        finally:
            # Removing client from client list
            with self.clients_lock:
                self.clients = [c for c in self.clients if c[1] != client_socket]

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

                for client_id, client_socket in current_clients:
                    try:

                        # We get the client_id from message, so we don't send to clients their own messages
                        parts = message.split(": ",1)
                        message_client_id = parts[0]
                        if client_id != message_client_id:
                            client_socket.send(f"{message}\n".encode('utf-8'))

                    except Exception as e:
                        # If sending fails, remove the client
                        with self.console_lock:
                            print(f"[SERVER] Failed to send to {client_id}: {e}")
                        with self.clients_lock:
                            self.clients = [c for c in self.clients if c[1] != client_socket]

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