#include <condition_variable>
#include <iostream>
#include <thread>
#include <mutex>
#include <random>
#include <vector>

using namespace std;

// n - wątków = filozofów
// n - widelców = zasobów
// Każdy filozof działa wdlg schematu: "myślenie-jedzenie-myslenie-...". Każdy etap jest skończony
// Aby zjeść filozof musi podnieś oba widelce, które znajdują się obok niego

// Wymagania
// Każdy z wątków raportuje o stanie w którym się znajduje (Wystarczy wydruk w konsoli)
//● W programie nie dochodzi do trwałego zablokowania wątków (ang. deadlock)
//● Program otrzymuje jako argument liczbę filozofów.

//Rozwiązanie:
// Filozofowie podnoszą najpierw lewy widelec, a potem prawy



// VARIABLES
int numPhilosophers; // number of philosophers
vector<mutex> forks;
vector<thread> philosophers;
mutex stateChangeMutex;
std::condition_variable cv;

//int thinkingTime = 2000; // 2 sekunda
//int eatingTime = 2000;  // 2 sekunda

std::mt19937 rng{std::random_device{}()};
uniform_int_distribution<int> thinkingTime{500, 2000};  // 0.5-2 sekundy
uniform_int_distribution<int> eatingTime{300, 1000};    // 0.3-1 sekunda

bool running = false;



// FUNCTION THINK AND EAT
void think(int ID) {
    {
        std::unique_lock<std::mutex> lock(stateChangeMutex);
        cout << "Phil "<< ID <<" is thinking" <<endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(thinkingTime(rng)));
    }
}

void eat(int ID) {
    // Philosopher starts eating with a left fork first,and a right fork second.
    // To avoid deadlock - the last philosopher is picking up right fork first.

    int leftFork = ID;
    int rightFork = (ID + 1) % numPhilosophers;

    if(ID == numPhilosophers - 1) {
        swap(leftFork, rightFork);
    }

    {
        std::unique_lock<std::mutex> lock(stateChangeMutex);
        cout << "Phil "<< ID <<" is trying to pick up forks" <<endl;
    }

    forks[leftFork].lock();
    {
        std::unique_lock<std::mutex> lock(stateChangeMutex);
        cout << "Phil "<< ID <<" picked up: leftFork" <<endl;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    forks[rightFork].lock();
    {
        std::unique_lock<std::mutex> lock(stateChangeMutex);
        std::cout << "Phil " << ID << " picked up: rightFork" << endl;
        std::cout << "Phil " << ID << " is eating\n";
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(eatingTime(rng)));
    // Putting forks away
    {
        std::unique_lock<std::mutex> lock(stateChangeMutex);
        cout << "Phil " << ID << " finished eating and puts forks away." <<endl;
    }
    forks[leftFork].unlock();
    forks[rightFork].unlock();

}

void run(int ID) {  // think and eat while program is running
    while (running) {
        think(ID);
        eat(ID);
    }
}

// MAIN
int main()
{
    cout << endl;
    cout << "----------------------------------------- "<< endl;
    cout << "Dining Philosophers Problem - Simulation." << endl;
    cout << "........................................." << endl;
    cout << endl;

    cout << "How many philosophers are going to eat?" << endl;
    cin >> numPhilosophers;
    if (numPhilosophers < 2) {
        cerr << "Philosophers number must be greater than 2" << endl;
    }else {
        running = true;
    }
    cout << endl;

    philosophers.resize(numPhilosophers);
    forks = std::vector<std::mutex>(numPhilosophers);

    cout << "Starting..." << endl;
    cout << "........................................." << endl;
    cout << endl;
    // Philosophers number is good, starting the simulation

    // Creating threads for each philosopher ->> they start work
    for(int i=0; i<numPhilosophers; i++) {
        philosophers[i] = thread(run, i);
    }

    // Waiting for the threads to complete the work
    for(auto& philosopher : philosophers) {
        philosopher.join();
    }

    return 0;
}
