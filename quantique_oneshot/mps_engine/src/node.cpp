#include "node.hpp"
#include <cmath>

namespace mps {

Node::Node() {
    A[0] = Eigen::MatrixXcd::Identity(1, 1);
    A[1] = Eigen::MatrixXcd::Zero(1, 1);
}

Node::Node(const Eigen::MatrixXcd& m0, const Eigen::MatrixXcd& m1) {
    A[0] = m0;
    A[1] = m1;
}

void Node::apply_1q_gate(const Eigen::Matrix2cd& gate) {
    Eigen::MatrixXcd old_0 = A[0];
    Eigen::MatrixXcd old_1 = A[1];
    A[0] = gate(0, 0) * old_0 + gate(0, 1) * old_1;
    A[1] = gate(1, 0) * old_0 + gate(1, 1) * old_1;
}

void Node::normalize() {
    double norm_sq = A[0].squaredNorm() + A[1].squaredNorm();
    if (norm_sq > 1e-20) {
        double n = std::sqrt(norm_sq);
        A[0] /= n;
        A[1] /= n;
    }
}

} // namespace mps
