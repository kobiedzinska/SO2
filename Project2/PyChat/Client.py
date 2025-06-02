import socket
import threading
import sys
import time

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True
        self.send_semaphore = threading.Semaphore(2)

    def start(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to server at {self.host}:{self.port}")
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            self.send_messages()
        except ConnectionRefusedError:
            print(f"[CLIENT] Connection refused. Server at {self.host}:{self.port} may not be running.")
        except Exception as e:
            print(f"[CLIENT] An error occurred: {e}")
        finally:
            self.shutdown()

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8').strip()
                if not message:
                    print("[CLIENT] Connection to server closed.")
                    self.running = False
                    break
                print(message)
            except (ConnectionResetError, Exception) as e:
                if self.running:
                    print(f"[CLIENT] Error receiving message: {e}")
                self.running = False
                break

    def send_messages(self):
        while self.running:
            try:
                message = input()
                if message.lower() == '/exit':
                    break
                self.send_semaphore.acquire()
                self.client_socket.send(message.encode('utf-8'))
                time.sleep(1)
                self.send_semaphore.release()
            except (BrokenPipeError, EOFError, KeyboardInterrupt, Exception) as e:
                if self.running:
                    print(f"[CLIENT] Error sending message: {e}")
                self.running = False
                break
        self.shutdown()

    def shutdown(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
                print("[CLIENT] Connection closed.")
            except Exception as e:
                print(f"[CLIENT] Error closing socket: {e}")
        sys.exit(0)

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    client = ChatClient(host, port)
    client.start()