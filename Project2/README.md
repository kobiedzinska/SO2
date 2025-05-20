# SO2 - Multithreaded chat server

Repozytorium projektów z kursu **Systemy Operacyjne 2**

## Opis projektu
Ten projekt implementuje wielowątkowy serwer czatu w języku Python, który umożliwia wielu klientom połączenie i komunikację w czasie rzeczywistym. Serwer wykorzystuje moduł threading do zarządzania wielowątkowością oraz ręcznie zaimplementowane mechanizmy ochrony sekcji krytycznych (mutexy, semafory) w celu zapewnienia bezpieczeństwa wątków i prawidłowej synchronizacji wiadomości między klientami.

## Kompilacja i uruchomienie
```bash
python chat_server.py [host] [port]
```
Defaultowe wartości, jeśli żadne nie zostaną podane:
host: 127.0.0.1 (localhost),
port: 8888

## Wątki i ich funkcje:
| Wątek   | funkcja         |
| ------ | ---------------- |
|nazwa_watku| funkcja |

- Czas myślenia i jedzenia każdego filozofa jest wartością losową pomiędzy 0.5 a 2 sekundami.

## Sekcje krytyczne 
| Sekcja krytyczna   | Rozwiązanie         |
| ------ | ---------------- |
| Wypisywanie do konsoli   | `std::unique_lock<std::mutex> lock(stateChangeMutex);`   |
| Podnoszenie i odkładanie zasobów (widelców)| `std::mutex` przypisany do każdego zasobu|

### Przykład zabezpieczenia sekcji:
```bash
{
    std::unique_lock<std::mutex> lock(stateChangeMutex);
    cout << "Phil " << ID << " is thinking" << endl;
}
```
## Rozwiązanie problemu zakleszczenia (deadlock)
- Ostatni filozof podnosi najpierw prawy widelec, a następnie lewy. => Eliminujemy wtedy cykliczne oczekiwanie.
```bash
if (ID == numPhilosophers - 1) {
    swap(leftFork, rightFork);
}
```
### 📎 Linki:
- dokumentacja 
