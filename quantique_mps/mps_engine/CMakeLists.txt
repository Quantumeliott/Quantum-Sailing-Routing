cmake_minimum_required(VERSION 3.10)
project(mps_engine)

set(CMAKE_CXX_STANDARD 17)

# LE CHEMIN QUE TU AS TROUVÉ AVEC BREW
set(EIGEN_INCLUDE_DIR "/opt/homebrew/opt/eigen/include/eigen3")

include_directories(${EIGEN_INCLUDE_DIR})
include_directories(include)

# Sources
set(SOURCES 
    src/node.cpp 
    src/mps.cpp 
    src/main.cpp
)

add_executable(simulator_test ${SOURCES})