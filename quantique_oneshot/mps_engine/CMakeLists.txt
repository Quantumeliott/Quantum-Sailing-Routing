cmake_minimum_required(VERSION 3.15)
project(mps_engine)

set(CMAKE_CXX_STANDARD 17)

# --- NOUVEAU : On force l'utilisation du Python système ---
set(PYBIND11_FINDPYTHON ON)
set(Python_EXECUTABLE /usr/local/bin/python3) 

# Chemins Eigen
set(EIGEN_PATH "/opt/homebrew/opt/eigen/include/eigen3")
include_directories(${EIGEN_PATH} include)

# Recherche de Pybind11
list(APPEND CMAKE_PREFIX_PATH "/opt/homebrew/opt/pybind11")
find_package(pybind11 REQUIRED)

# Création du module
pybind11_add_module(mps_engine 
    src/node.cpp 
    src/mps.cpp 
    src/wrapper.cpp
)