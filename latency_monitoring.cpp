#include <chrono>
using namespace std::chrono;

class LatencyMonitor {
public:
    void start() {
        start_time = high_resolution_clock::now();
    }

    int64_t stop() {
        auto end_time = high_resolution_clock::now();
        return duration_cast<microseconds>(end_time - start_time).count();
    }

private:
    high_resolution_clock::time_point start_time;
};

// Utilization in a trading engine:
LatencyMonitor lm;
lm.start();
place_order();
int64_t latency = lm.stop(); // Delay in microseconds
