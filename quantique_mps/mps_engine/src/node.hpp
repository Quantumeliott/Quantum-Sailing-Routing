#pragma once
#include <Eigen/Dense>
#include <complex>

namespace mps {

class Node {
public:
    // |node> = A[0] |0> + A[1] |1>
    Eigen::MatrixXcd A[2]; 

    Node();
    Node(const Eigen::MatrixXcd& m0, const Eigen::MatrixXcd& m1);

    int left_dim()  const { return (int)A[0].rows(); }
    int right_dim() const { return (int)A[0].cols(); }

    void apply_1q_gate(const Eigen::Matrix2cd& gate);
    void normalize();
};

} // namespace mps
