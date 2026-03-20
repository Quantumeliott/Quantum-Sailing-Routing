#pragma once
#include "node.hpp"
#include "gate.hpp"
#include <vector>
#include <string>

namespace mps {

class MPS {
private:
    int num_qubits;
    int max_bond_dim;
    std::vector<Node> nodes;

public:
    MPS(int n, int chi_max = 64);

    void apply_gate(const std::string& name, int target, double theta = 0.0);
    
    void apply_cnot(int control, int target);

    double compute_expectation_z(int target);

    double compute_expectation_zz(int q1, int q2);

    void apply_swap(int i);
};

} // namespace mps