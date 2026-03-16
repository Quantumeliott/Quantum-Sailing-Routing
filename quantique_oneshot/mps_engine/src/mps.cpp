#include "mps.hpp"
#include <Eigen/SVD>
#include <iostream>
#include <algorithm>

namespace mps {

// --- 1. CONSTRUCTEUR ---
MPS::MPS(int n, int chi_max) : num_qubits(n), max_bond_dim(chi_max) {
    Eigen::MatrixXcd m0(1, 1); m0(0,0) = 1.0;
    Eigen::MatrixXcd m1(1, 1); m1(0,0) = 0.0;

    for(int i=0; i<n; ++i) {
        nodes.emplace_back(m0, m1);
    }
}

// --- 2. PORTES À 1 QUBIT ---
void MPS::apply_gate(const std::string& name, int target, double theta) {
    if (target < 0 || target >= num_qubits) return;

    if (name == "H") nodes[target].apply_1q_gate(Gates::H);
    else if (name == "X") nodes[target].apply_1q_gate(Gates::X);
    else if (name == "RX") nodes[target].apply_1q_gate(Gates::RX(theta));
    else if (name == "RZ") nodes[target].apply_1q_gate(Gates::RZ(theta));
}

// --- 3. UTILITAIRE ---
void MPS::print_dimensions() const {
    for(int i=0; i<num_qubits; ++i) {
        std::cout << "[" << nodes[i].left_dim() << "x" << nodes[i].right_dim() << "] ";
    }
    std::cout << std::endl;
}

// --- 4. PORTE CNOT (AVEC SVD & COMPRESSION) ---
void MPS::apply_cnot(int i, int j) {
    if (std::abs(i - j) != 1) return; // Uniquement voisins pour l'instant

    int left = std::min(i, j);
    int right = std::max(i, j);

    int chiL = nodes[left].left_dim();
    int chiR = nodes[right].right_dim();

    // Contraction
    Eigen::MatrixXcd theta = Eigen::MatrixXcd::Zero(2 * chiL, 2 * chiR);
    for (int sL = 0; sL < 2; ++sL) {
        for (int sR = 0; sR < 2; ++sR) {
            theta.block(sL * chiL, sR * chiR, chiL, chiR) = nodes[left].A[sL] * nodes[right].A[sR];
        }
    }

    // Application du CNOT
    Eigen::MatrixXcd theta_prime = Eigen::MatrixXcd::Zero(2 * chiL, 2 * chiR);
    for (int a = 0; a < 2; ++a) {
        for (int b = 0; b < 2; ++b) {
            for (int sL = 0; sL < 2; ++sL) {
                for (int sR = 0; sR < 2; ++sR) {
                    theta_prime.block(a * chiL, b * chiR, chiL, chiR) += 
                        Gates::CNOT(a * 2 + b, sL * 2 + sR) * theta.block(sL * chiL, sR * chiR, chiL, chiR);
                }
            }
        }
    }

    // SVD (Syntaxe moderne pour éviter le warning 'deprecated')
    Eigen::BDCSVD<Eigen::MatrixXcd, Eigen::ComputeThinU | Eigen::ComputeThinV> svd(theta_prime);
    
    auto S = svd.singularValues();
    auto U = svd.matrixU();
    auto V = svd.matrixV().adjoint();

    int new_chi = std::min({(int)S.size(), max_bond_dim});

    // Mise à jour des noeuds
    nodes[left].A[0] = U.block(0, 0, chiL, new_chi);
    nodes[left].A[1] = U.block(chiL, 0, chiL, new_chi);

    Eigen::MatrixXcd SV = S.head(new_chi).asDiagonal() * V.block(0, 0, new_chi, 2 * chiR);
    nodes[right].A[0] = SV.block(0, 0, new_chi, chiR);
    nodes[right].A[1] = SV.block(0, chiR, new_chi, chiR);

    nodes[left].normalize();
    nodes[right].normalize();
}
// =========================================================================
// CALCULS DES VALEURS D'ATTENTE (EXACTES VIA CONTRACTION EIGEN)
// =========================================================================

double MPS::compute_expectation_z(int target) {
    if (target < 0 || target >= num_qubits) return 0.0;

    // E est la matrice d'environnement (démarre à 1x1)
    Eigen::MatrixXcd E = Eigen::MatrixXcd::Identity(1, 1);
    Eigen::MatrixXcd NormE = Eigen::MatrixXcd::Identity(1, 1);

    for (int k = 0; k < num_qubits; ++k) {
        int next_dim = nodes[k].A[0].cols();
        Eigen::MatrixXcd next_E = Eigen::MatrixXcd::Zero(next_dim, next_dim);
        Eigen::MatrixXcd next_NormE = Eigen::MatrixXcd::Zero(next_dim, next_dim);

        for (int s = 0; s < 2; ++s) {
            double O_val = 1.0;
            if (k == target) {
                O_val = (s == 0) ? 1.0 : -1.0; // Opérateur Z
            }

            // Contraction Eigen: A_s^\dagger * E * A_s
            Eigen::MatrixXcd A_adj = nodes[k].A[s].adjoint();
            next_E += O_val * A_adj * E * nodes[k].A[s];
            next_NormE += A_adj * NormE * nodes[k].A[s]; // Pour garder la norme exacte
        }
        E = next_E;
        NormE = next_NormE;
    }

    // Le résultat est le scalaire final, normalisé
    return E(0, 0).real() / NormE(0, 0).real();
}

double MPS::compute_expectation_zz(int q1, int q2) {
    if (q1 < 0 || q1 >= num_qubits || q2 < 0 || q2 >= num_qubits) return 0.0;
    if (q1 == q2) return 1.0; // Z * Z = I

    Eigen::MatrixXcd E = Eigen::MatrixXcd::Identity(1, 1);
    Eigen::MatrixXcd NormE = Eigen::MatrixXcd::Identity(1, 1);

    for (int k = 0; k < num_qubits; ++k) {
        int next_dim = nodes[k].A[0].cols();
        Eigen::MatrixXcd next_E = Eigen::MatrixXcd::Zero(next_dim, next_dim);
        Eigen::MatrixXcd next_NormE = Eigen::MatrixXcd::Zero(next_dim, next_dim);

        for (int s = 0; s < 2; ++s) {
            double O_val = 1.0;
            // On applique Z si on est sur q1 OU q2
            if (k == q1 || k == q2) {
                O_val = (s == 0) ? 1.0 : -1.0;
            }

            Eigen::MatrixXcd A_adj = nodes[k].A[s].adjoint();
            next_E += O_val * A_adj * E * nodes[k].A[s];
            next_NormE += A_adj * NormE * nodes[k].A[s];
        }
        E = next_E;
        NormE = next_NormE;
    }
    return E(0, 0).real() / NormE(0, 0).real();
}
void MPS::apply_swap(int i) {
    if (i < 0 || i >= num_qubits - 1) return;

    int left = i;
    int right = i + 1;
    int chiL = nodes[left].left_dim();
    int chiR = nodes[right].right_dim();

    // 1. Contraction
    Eigen::MatrixXcd theta = Eigen::MatrixXcd::Zero(2 * chiL, 2 * chiR);
    for (int sL = 0; sL < 2; ++sL) {
        for (int sR = 0; sR < 2; ++sR) {
            theta.block(sL * chiL, sR * chiR, chiL, chiR) = nodes[left].A[sL] * nodes[right].A[sR];
        }
    }

    // 2. SWAP physique (on inverse les probabilités sL et sR)
    Eigen::MatrixXcd theta_prime = Eigen::MatrixXcd::Zero(2 * chiL, 2 * chiR);
    for (int sL = 0; sL < 2; ++sL) {
        for (int sR = 0; sR < 2; ++sR) {
            theta_prime.block(sR * chiL, sL * chiR, chiL, chiR) = theta.block(sL * chiL, sR * chiR, chiL, chiR);
        }
    }

    // 3. SVD
    Eigen::BDCSVD<Eigen::MatrixXcd, Eigen::ComputeThinU | Eigen::ComputeThinV> svd(theta_prime);
    auto S = svd.singularValues();
    auto U = svd.matrixU();
    auto V = svd.matrixV().adjoint();

    int new_chi = std::min({(int)S.size(), max_bond_dim});

    // 4. Mise à jour des noeuds
    nodes[left].A[0] = U.block(0, 0, chiL, new_chi);
    nodes[left].A[1] = U.block(chiL, 0, chiL, new_chi);

    Eigen::MatrixXcd SV = S.head(new_chi).asDiagonal() * V.block(0, 0, new_chi, 2 * chiR);
    nodes[right].A[0] = SV.block(0, 0, new_chi, chiR);
    nodes[right].A[1] = SV.block(0, chiR, new_chi, chiR);

    nodes[left].normalize();
    nodes[right].normalize();
}
}