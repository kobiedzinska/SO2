# SO2 - Dining Philosophers Problem

Repozytorium projektów z kursu **Systemy Operacyjne 2**

## Opis projektu
Projekt jest implementacją klasycznego problemu **„Ucztujących Filozofów”** z użyciem:
- `std::thread`
- `std::mutex`

Symulacja ilustruje zarządzanie  współbieznym dostępem do zasobów (forks) i rozwiązuje problem zakleczenia (deadlock).

## Kompilacja i uruchomienie
```bash
g++ -std=c++20 -pthread philosophers.cpp -o philosophers
./philosophers
```

## Wątki i ich funkcje:
| Wątek   | funkcja         |
| ------ | ---------------- |
| Philosopher   | Każdy wątek reprezentuje filozofa. W pętli wykonuje think(ID) i eat(ID) dopóki running = true.   |

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
- dokumentacja `std::mutex`: https://en.cppreference.com/w/cpp/thread/mutex
