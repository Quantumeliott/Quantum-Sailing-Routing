#pragma once
#include <Eigen/Dense>
#include <complex>
#include <cmath>

namespace mps {

using namespace std::complex_literals;

struct Gates {
    //Identity
    inline static const Eigen::Matrix2cd I = Eigen::Matrix2cd::Identity();

    //Not
    inline static const Eigen::Matrix2cd X = (Eigen::Matrix2cd() << 0, 1, 1, 0).finished();

    //Hadamard
    inline static const Eigen::Matrix2cd H = (Eigen::Matrix2cd() << 1.0/std::sqrt(2),  1.0/std::sqrt(2),
                                                                   1.0/std::sqrt(2), -1.0/std::sqrt(2)).finished();

    // Rotation on X
    static Eigen::Matrix2cd RX(double theta) {
        Eigen::Matrix2cd m;
        m << std::cos(theta/2.0), -1.0i * std::sin(theta/2.0),
             -1.0i * std::sin(theta/2.0), std::cos(theta/2.0);
        return m;
    }

    // Rotation on Z
    static Eigen::Matrix2cd RZ(double theta) {
        Eigen::Matrix2cd m;
        m << std::exp(-1.0i * theta/2.0), 0,
             0, std::exp(1.0i * theta/2.0);
        return m;
    }

    // CNOT
    inline static const Eigen::Matrix4cd CNOT = (Eigen::Matrix4cd() << 1, 0, 0, 0,
                                                                      0, 1, 0, 0,
                                                                      0, 0, 0, 1,
                                                                      0, 0, 1, 0).finished();

    // CNOT inversé (Qubit de droite contrôle qubit de gauche)
    inline static const Eigen::Matrix4cd CNOT_REV = (Eigen::Matrix4cd() << 1, 0, 0, 0,
                                                                           0, 0, 0, 1,
                                                                           0, 0, 1, 0,
                                                                           0, 1, 0, 0).finished();
};

} // namespace mps
