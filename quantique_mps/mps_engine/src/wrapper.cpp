#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mps.hpp"

namespace py = pybind11;

PYBIND11_MODULE(mps_engine, m) {
    m.doc() = "Moteur de simulation MPS haute performance";

    py::class_<mps::MPS>(m, "MPS")
        .def(py::init<int, int>(),
             py::arg("n"), py::arg("chi_max") = 64)
        .def("apply_gate",&mps::MPS::apply_gate,
             py::arg("name"), py::arg("target"), py::arg("theta") = 0.0)
        .def("apply_cnot",&mps::MPS::apply_cnot)
        .def("expectation_z",&mps::MPS::compute_expectation_z)
        .def("apply_swap", &mps::MPS::apply_swap)
        .def("expectation_zz", &mps::MPS::compute_expectation_zz);
}
