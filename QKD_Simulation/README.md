# Quantum Key Distribution (QKD) Protocol Simulation with NetSquid

This repository provides **implementations and simulations of BB84, E91, and MDI-QKD quantum key distribution protocols** using the [NetSquid](https://netsquid.org/) discrete-event simulator.  
It is designed as a **research-oriented toolset** to simulate **realistic quantum communication networks**, focusing on **physical-layer imperfections, fiber-channel noise, and measurement device limitations**.  

---

## 🎯 Motivation

During my final year research project, I identified a major challenge in QKD research:  
> **There were no publicly available, accurate, and realistic QKD simulation codes.**  

Most open-source QKD simulators:  
- **Ignore realistic channel noise and photon loss**  
- **Simplify QKD logic** without true physical modeling  
- Lack modularity for research-level extension  

Implementing QKD experimentally requires **expensive hardware**:
- Single-photon sources, detectors, and entanglement devices  
- Precision optical fiber setups  
- Sophisticated synchronization and error correction systems  

This project was built to **bridge that gap** by providing:  
- **Physically realistic QKD simulations**  
- **Customizable models** of quantum devices and channels  
- **Research-ready modular code** for extending QKD protocols  

---

## 🗂 Repository Structure

| Set                  | Description |
|----------------------|------------|
| **Advanced Set**     | Modular implementation with **device-level customization** and **detailed noise models**. Ideal for research experiments. |
| **Basic Set**        | Lightweight, single-file implementations for quick **demonstrations and testing**. Beginner-friendly. |

Both sets support **performance visualization** with **plots** (e.g., QBER, throughput) for a **10 km optical link**.

---

## 🔧 Technical Details

- **Simulator**: [NetSquid](https://netsquid.org/)  
- **NetSquid Version Used**: `1.1.1`  
- **Programming Language**: Python 3.x  
- **Core Dependencies**:  
  - `netsquid`  
  - `numpy`  
  - `matplotlib`  

---

## 🔬 Simulator Comparison

| Feature                               | NetSquid                                                                                   | QuNetSim                                                | SimulaQron                                         | Qiskit/Cirq                                          |
|--------------------------------------|-------------------------------------------------------------------------------------------|--------------------------------------------------------|--------------------------------------------------|------------------------------------------------------|
| **Simulation Approach**              | Discrete-event simulation with detailed physical modeling                                  | High-level Python interface for protocol design         | Application-focused, limited low-level modeling  | Quantum circuit paradigm (gate/circuit simulation)   |
| **Physical Layer Realism**           | High: Supports hardware imperfections, photon loss, qubit decoherence                     | Low: High abstraction, not physics-focused             | Low: Minimal physics modeling                     | Low: Focused on circuit logic, not networks         |
| **Scalability**                      | High: Designed for large network simulations                                              | Moderate: Suitable for small-scale networks            | Limited: Application development focus            | Limited: Focused on individual circuits             |
| **Key Advantage for QKD Research**   | Essential for simulating **hardware noise** & **channel imperfections**                  | Good for simple network logic                          | Minimal support for physical realism             | Not designed for network-level QKD simulations      |

> **Why NetSquid?** I selected NetSquid because of its **high physical-layer realism, noise modeling, and scalability**, making it ideal for accurately simulating QKD protocols and quantum network imperfections.

---

## 🧩 Implemented QKD Protocols

| Protocol | Description | Reference |
|----------|-------------|-----------|
| **BB84** | The first QKD protocol (Bennett & Brassard, 1984), using **photon polarization states** to generate secure keys. | [Comprehensive Study of BB84](https://www.researchgate.net/publication/370040044_Comprehensive_Study_of_BB84_A_Quantum_Key_Distribution_Protocol) |
| **E91**  | Uses **entangled photon pairs** and Bell inequality tests for security verification, resistant to eavesdropping. | [Wikipedia - E91 Protocol](https://en.wikipedia.org/wiki/Quantum_key_distribution#E91_protocol:_Artur_Ekert_.281991.29) |
| **MDI-QKD** | Measurement-Device-Independent QKD eliminates detector side-channel attacks via a **Bell-state measurement (BSM)** node. | [arXiv:1109.1473](https://arxiv.org/abs/1109.1473) |

---

## 🌐 Simulation Network Setup

The simulations are configured for a **10 km optical fiber channel** between **Alice** and **Bob**, with the following roles:

- **Alice**: Prepares and transmits qubits using a quantum processor.  
- **Bob**: Measures incoming qubits using a quantum processor.  
- **Charlie (MDI-QKD)**: Performs **Bell-State Measurement (BSM)** to detect entanglement using a **CNOT + Hadamard measurement** sequence.  
- **Entanglement Source**: Generates entangled photon pairs for protocols like E91.  
- **Bell Parameter**: Derived from CHSH Bell inequality tests to verify non-classical correlations.  

---

## ⚙️ Realistic Physical Models

This project includes **advanced noise and device models** to simulate real-world constraints:

| Model                              | Description |
|-----------------------------------|-------------|
| **Fiber Delay Model**             | Simulates finite speed of light in optical fiber (`c = 2 × 10^5 km/s`). |
| **Fiber Loss Model**              | Implements probabilistic qubit loss (`p_loss_length = 0.2`, meaning **0.2 dB/km attenuation**). |
| **Depolarization Noise Model**    | Applies qubit depolarization noise (`depolar_rate = 0.01`). |
| **Classical Communication**       | Simulates **basis exchange messages** and tracks **communication overhead**. |
| **Random Basis Generator**        | Creates random basis sequences for Alice and Bob (0/1 bit encoding). |
| **Bell-State Measurement (BSM)**  | Charlie node detects entangled states via **CNOT-Hadamard measurement sequences**. |

These features allow **realistic performance evaluation** of QKD protocols in fiber networks.

---

## 📊 Performance Metrics

| Metric                        | Definition |
|-------------------------------|-----------|
| **Throughput (qubits/sec)**  | Number of successfully transmitted qubits per second. |
| **Synchronization Time (ms)**| Time required to synchronize Alice and Bob’s measurement bases. |
| **Raw Key Rate (qubits)**    | Amount of raw key material before error correction. |
| **QBER (%)**                 | Quantum Bit Error Rate; lower values indicate better channel quality. |
| **Latency (ms)**             | Total delay in qubit transmission and key generation. |
| **Communication Overhead**   | Number of classical messages exchanged for authentication and error correction. |
| **Channel Loss Rate (%)**    | Percentage of qubits lost during transmission. |

Example -

![Throughput Comparison](https://github.com/bulithakawushika/QKD-Protocol-Simulation-with-NetSquid/blob/main/Advanced%20Protocol%20Set/Sample%20Results%20Plots/A1%20-%20Throughput%20Comparison.png)

---

## 🔒 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📚 Further Reading

- [NetSquid Documentation](https://netsquid.org/docs/latest-release/)  
- [Comprehensive Study of BB84 Protocol](https://www.researchgate.net/publication/370040044_Comprehensive_Study_of_BB84_A_Quantum_Key_Distribution_Protocol)  
- [E91 Protocol - Wikipedia](https://en.wikipedia.org/wiki/Quantum_key_distribution#E91_protocol:_Artur_Ekert_.281991.29)  
- [Measurement-Device-Independent QKD - arXiv:1109.1473](https://arxiv.org/abs/1109.1473)  
