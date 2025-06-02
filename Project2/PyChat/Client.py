import socket
import threading
import sys
import time

class ChatClient:
    def __init__(self, host, port):
        self.host = host # Server IP address
        self.port = port # Server port number
        self.client_socket = None # Socket object for the client
        self.running = True # Flag to control the main loop
        self.send_semaphore = threading.Semaphore(2) # Allows up to 2 simultaneous sends

    def start(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to server at {self.host}:{self.port}")

            receive_thread = threading.Thread(target=self.receive_messages) # Create a thread for receiving messages
            receive_thread.daemon = True # Allow the main thread to exit even if this thread is running
            receive_thread.start()

            self.send_messages()# Start sending messages

        except ConnectionRefusedError:
            print(f"[CLIENT] Connection refused. Server at {self.host}:{self.port} may not be running.")
        except Exception as e:
            print(f"[CLIENT] An error occurred: {e}")
        finally:
            self.shutdown() # Clean up resources

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8').strip() # Receive data from the server
                if not message: # If no data is received, the connection closed
                    print("[CLIENT] Connection to server closed.")
                    self.running = False
                    break
                print(message)
            except ConnectionResetError:
                print("[CLIENT] Connection to server was reset.")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"[CLIENT] Error receiving message: {e}")
                self.running = False
                break

    def send_messages(self):
        while self.running:
            try:
                message = input()
                if message.lower() == '/exit': # If the user types '/exit', break the loop
                    break
                self.send_semaphore.acquire() #
                self.client_socket.send(message.encode('utf-8')) # Send the message to the server
                time.sleep(1) # Artificial delay to demonstrate the semaphore's effect
                self.send_semaphore.release()
            except BrokenPipeError:
                print("[CLIENT] Connection to server lost while sending.")
                self.running = False
                break
            except EOFError:
                print("[CLIENT] EOFError.")
                self.running = False
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.running:
                    print(f"[CLIENT] Error sending message: {e}")
                self.running = False
                break
        self.shutdown() # Clean up resources after sending is done

    def shutdown(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
                print("[CLIENT] Connection closed.")
            except Exception as e:
                print(f"[CLIENT] Error closing socket: {e}")
        sys.exit(0) # Exit the program

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1' # Get host from command line arguments or use default
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888 # Get port from command line arguments or use default

    client = ChatClient(host, port)
    client.start()