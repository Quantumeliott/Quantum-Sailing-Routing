#  Quantum Sailing Routing/Race

This project is my first big step into quantum computing and the Quantum Approximate Optimization Algorithm (QAOA)! 

My goal was to build a QAOA from scratch and optimize it to create the best possible routing algorithm. My idea was to create a sailboat race with a visual rendering (you can see a simulation in the `output.mp4` video) and complex, dynamic weather. To measure the performance of the algorithms, we organize a race between the boats, and the best one wins!

##  The Three Participants

* 🔵 **Classique (Dijkstra)**: Always the fastest one (as Dijkstra is mathematically perfect for this kind of problem). It acts as the ultimate baseline for our routing solutions.
* 🟠 **Quantum (QAOA Standard)**: Our first hybrid algorithm using Qiskit's standard statevector simulation.
* 🔴 **Quantum_mps**: Our second hybrid algorithm, powered by a custom C++ Matrix Product State (MPS) engine.

## Project Logbook / Feedback

I began by creating the visual environment, the dynamic weather, and all the UI elements you can see in the video. Then, I programmed the Dijkstra algorithm, which wasn't too difficult as it is a very standard approach for this type of pathfinding problem.

Next, I started thinking about the QAOA architecture: how to model the problem with the Ising model to get a Hamiltonian to minimize, how to actually minimize it, and especially how to be efficient when limited to only 15 qubits (representing the path). Using standard quantum libraries like Qiskit felt a bit limiting because built-in functions (like the statevector simulator) hide the underlying complexity and hit a hardware wall very quickly.

So, I decided to dive into the deep end. This allowed me to truly understand how everything works under the hood and to break the qubit limit barrier: I created a C++ quantum engine from scratch.

**The Tensor Network Revolution:**
To bypass the memory limitations of standard simulators, we abandoned naive simulation and coded **our own C++ quantum engine based on Matrix Product States (MPS)**.
* Instead of storing the entire quantum universe, the engine "compresses" entanglement on the fly using advanced mathematics (SVD).
* The Python code handles **dynamic routing** by inserting `SWAP` gates on the fly to adapt the geographical graph to the 1D topology of the C++ engine.
* **Result:** The boat can simulate giant graphs on a simple laptop and make long-term strategic decisions!

The new challenge is balancing the size of the graphs, the ability of the classical optimizer (COBYLA) to find the right path, and the computation time. Now our boat has a much broader vision, even if the quantum noise sometimes makes it choose surprising paths.

## How to run the race?

### Prerequisites
Make sure you have Python 3.x, a C++ compiler (GCC/Clang), and CMake installed on your machine.

First, install the required Python dependencies:
```bash
pip install numpy pandas matplotlib networkx qiskit qiskit-algorithms qiskit-optimization scipy pybind11 pygame