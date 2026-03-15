#include "../include/mps.hpp"
#include <iostream>

namespace mps {

MPS::MPS(int n, int chi_max) : num_qubits(n), max_bond_dim(chi_max) {
    Eigen::MatrixXcd m0(1, 1); m0(0,0) = 1.0;
    Eigen::MatrixXcd m1(1, 1); m1(0,0) = 0.0;

    for(int i=0; i<n; ++i) {
        nodes.emplace_back(m0, m1);
    }
}

void MPS::apply_gate(const std::string& name, int target, double theta) {
    if (target < 0 || target >= num_qubits) return;

    if (name == "H") nodes[target].apply_1q_gate(Gates::H);
    else if (name == "X") nodes[target].apply_1q_gate(Gates::X);
    else if (name == "RX") nodes[target].apply_1q_gate(Gates::RX(theta));
    else if (name == "RZ") nodes[target].apply_1q_gate(Gates::RZ(theta));
}

void MPS::print_dimensions() const {
    for(int i=0; i<num_qubits; ++i) {
        std::cout << "[" << nodes[i].left_dim() << "x" << nodes[i].right_dim() << "] ";
    }
    std::cout << std::endl;
}

void MPS::apply_cnot(int control, int target) {
    // TODO: La fameuse SVD arrive ici !
    std::cout << "CNOT non encore implemente (SVD requise)" << std::endl;
}

} // namespace mps