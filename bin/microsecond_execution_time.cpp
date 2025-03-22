auto start = std::chrono::high_resolution_clock::now();
place_order();
auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
std::cout << "Order latency: " << duration.count() << "μs\n";
