# Quantum Sailboat Routing: QAOA vs. Dijkstra 


## Project Overview

Navigating a sailboat efficiently requires constantly adapting to dynamic wind fields (speed and direction). This project simulates a live weather environment where two algorithms race to find the fastest route to a destination :

* **The Classical Approach (Dijkstra):** Acts as a global optimizer. It computes the entire journey at t=0, perfectly anticipating future weather changes across the entire map.

* **The Quantum Approach (QAOA):** Acts as a local, receding-horizon optimizer. Due to current hardware and simulation constraints regarding the number of qubits, the QAOA generates a localized "macro-graph" at each step. It solves a smaller QUBO (Quadratic Unconstrained Binary Optimization) problem to determine its immediate optimal heading.

##  Key Features

* **Dynamic Wind Simulation:** Real-time generation of wind fields using animated noise layers (Synoptic weather patterns).
* **Quantum Simulation:** Custom QAOA implementation using IBM's Qiskit `StatevectorSampler` and `COBYLA` optimizer, featuring on-the-fly circuit transpilation to bypass matrix bottlenecks.
* **Interactive UI:** A custom Matplotlib-based dashboard featuring a time-synced animated race between the classical and quantum boats, complete with CPU computation times and simulated race times.
* **Replay Mode:** A time-slider allows users to review the race frame-by-frame and analyze algorithmic decision-making.

## Limits
My goal was to optimize a maximum the QAOA so that he could compete with dijkstra but the limits of qubits is extremely restrictive. I had to choose to create graphs that 

##  Getting Started

### Prerequisites
To run the project you just have to execute the main file and to download the following
libraries.
Ensure you have Python 3 installed along with the required scientific and quantum libraries:
 

```bash
pip install numpy pandas matplotlib networkx qiskit qiskit-algorithms qiskit-optimization scipy

