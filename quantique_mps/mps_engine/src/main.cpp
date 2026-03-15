#include "../include/mps.hpp"
#include <iostream>

int main() {
    mps::MPS sim(10, 64);
    
    std::cout << "Initial state dims: ";
    sim.print_dimensions();

    sim.apply_gate("H", 0);
    sim.apply_gate("RX", 1, 1.57);

    std::cout << "State after 1-qubit gates: ";
    sim.print_dimensions();

    return 0;
}