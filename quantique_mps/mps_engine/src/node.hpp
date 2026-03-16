#pragma once
#include <Eigen/Dense>
#include <complex>

namespace mps {

class Node {
public:
    Eigen::MatrixXcd A[2]; // A[0] pour |0>, A[1] pour |1>

    Node();
    Node(const Eigen::MatrixXcd& m0, const Eigen::MatrixXcd& m1);

    int left_dim()  const { return (int)A[0].rows(); }
    int right_dim() const { return (int)A[0].cols(); }

    void apply_1q_gate(const Eigen::Matrix2cd& gate);
    void normalize();
};

} // namespace mps
