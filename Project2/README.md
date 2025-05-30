# SO2 - Multithreaded chat server

Repozytorium projektów z kursu **Systemy Operacyjne 2**

## Opis projektu
Ten projekt implementuje wielowątkowy serwer czatu w języku Python, który umożliwia wielu klientom połączenie i komunikację w czasie rzeczywistym. Serwer wykorzystuje moduł threading do zarządzania wielowątkowością oraz ręcznie zaimplementowane mechanizmy ochrony sekcji krytycznych (mutexy, semafory) w celu zapewnienia bezpieczeństwa wątków i prawidłowej synchronizacji wiadomości między klientami.

## Kompilacja i uruchomienie
### Serwer
```bash
python server.py [host] [port]
```
### Klient
```bash
python client.py [host] [port]
```
Defaultowe wartości, jeśli żadne nie zostaną podane:
host: 127.0.0.1 (localhost),
port: 8888

## Wątki i ich funkcje:
### Serwer
| Wątek   | funkcja         | Opis    |
| ------ | ---------------- |---------|
| główny wątek | start() | Akceptuje połączenia i uruchamia serwer|
| zajmowanie się klientem | handle_client() | Obsługuje komunikację z pojedynczym klientem |
| zajmowanie się wiadomościami | dispatch_messages() | Odpowiada za rozsyłanie wiadomości do wszystkich klientów |

### Klient
| Wątek   | funkcja         | Opis    |
| ------ | ---------------- |---------|

## Sekcje krytyczne 
| Sekcja  | Blokada   | Powód użycia |
| ------ | ---------------- | -------- |
| clients   | clients_lock (threading.Lock) | Lista klientów może być modyfikowana przez wiele wątków |
| print() oraz komunikaty na konsoli | console_lock (threading.Lock) | Jednoczesne wypisywanie tekstu na konsolę przez wiele wątków |
| Kolejka wiadomości message_queue | none | queue.Queue jest bezpieczna dla wątków, nie wymaga dodatkowej blokady |

### Przykład zabezpieczenia sekcji:
```python
with self.clients_lock:
self.clients.append((client_id, client_socket))
```
## Semafory
| Semafor | Wartość | Cel użycia |
|---------| -------- | ---------- |
| connection_semaphore | 5 (max_connections) | Ogranicza liczbę jednoczesnych klientów do max_connections|

### Przykład użycia semafora:
```python
if self.connection_semaphore.acquire(blocking=False):
    try:
        client_socket, client_address = self.server_socket.accept()
        # ...
    except Exception as e:
        self.connection_semaphore.release()  # Releasing if there's error
else:
    print("[SERVER] Max connections reached, waiting...")
    threading.Event().wait(5.0)  # waiting 5 seconds
```

### 📎 Linki:
- threading https://docs.python.org/3/library/threading.html#
- socket https://docs.python.org/3/howto/sockets.html
- queue https://docs.python.org/3/library/queue.html
