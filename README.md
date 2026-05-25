# Comparative Benchmarking of QKD Protocols: BB84, E91, and MDI-QKD

> **Academic Project** — Quantum Computing Course, Spring 2026  
> Simulation-based benchmarking of Quantum Key Distribution protocols over realistic optical fibre channels.

---

## 📄 Base Paper

This project implements and extends the simulation methodology described in:

> **"Quantum Network Simulation and Emulation: A Roadmap for Quantum Internet Design"**  
> Brian Doolittle, Michael Cubeddu — *arXiv:2603.01980v1* (2026)  
> [📥 PDF included in repository](2603.01980v1%20(1).pdf)

The paper provides a roadmap for quantum network simulation, covering physical-layer modelling, noise characterisation, and protocol evaluation. Our work implements this roadmap concretely by building, running, and benchmarking three major QKD protocols under identical realistic channel conditions.

---

## 🎯 Proposed Methodology

Most open-source QKD comparisons test protocols in isolation or under idealised conditions, making fair comparison impossible. Our proposed methodology is a **simulation-based comparative benchmark** that:

1. **Implements all three protocols** (BB84, E91, MDI-QKD) under **identical physical channel conditions** — same distance, same loss model, same noise model.
2. **Runs 30 independent simulations** per protocol to capture statistical distributions rather than single-point estimates.
3. **Measures 8 standardised performance metrics** consistently across all protocols.
4. **Conducts a distance sweep** (1–50 km) to evaluate scalability and degradation behaviour.
5. **Produces comparative visualisations** (box plots, radar charts, heatmaps, distance analysis) to surface trade-offs clearly.

This enables an **apples-to-apples comparison** of security level, efficiency, and overhead across the three dominant QKD paradigms.

---

## 🔬 Protocols Implemented

| Protocol | Security Basis | Key Feature |
|----------|---------------|-------------|
| **BB84** | Quantum no-cloning theorem | Original QKD protocol; uses photon polarisation; highest efficiency |
| **E91** | Bell inequality violation (CHSH) | Entanglement-based; provides quantum-mechanical security proof |
| **MDI-QKD** | Measurement-device-independent | Eliminates detector side-channel attacks via Bell-State Measurement node |

Each protocol is implemented at **two levels**:
- **Basic Set** — pure Python, no external quantum simulator; fast, portable
- **Advanced Set** — [NetSquid](https://netsquid.org/) discrete-event simulation with hardware-level noise models

---

## 📊 Results & Findings

All experiments use a **10 km optical fibre channel** with:
- Fibre loss: `0.2 dB/km` (standard SMF-28)
- Depolarisation noise rate: `0.8%`
- Initial photon loss: `0.1 dB`
- Speed of light in fibre: `1.9 × 10⁵ km/s`

### Numerical Summary (mean ± SD, 30 runs @ 10 km)

| Metric | BB84 | E91 | MDI-QKD |
|--------|------|-----|---------|
| **Raw Key Rate (bits)** | **170.2 ± 11.2** | 29.6 ± 3.7 | 19.7 ± 2.3 |
| **QBER (%)** | **0.00 ± 0.00** | **0.00 ± 0.00** | 4.33 ± 1.97 |
| **Latency (ms)** | **1.03 ± 0.02** | 1.05 ± 0.05 | 1.43 ± 0.13 |
| **Channel Loss Rate (%)** | 38.5 ± 1.3 | 72.1 ± 1.5 | 39.7 ± 1.3 |
| **Throughput (bits/s)** | **164,835 ± 10,324** | 28,373 ± 3,495 | 13,850 ± 1,751 |
| **Comm. Overhead (msgs)** | **51 ± 0** | 131 ± 0 | 593 ± 12 |
| **Sync. Time (ms)** | **1.26 ± 0.00** | 1.52 ± 0.00 | 2.85 ± 0.00 |
| **Comp. Time/Round (ns)** | **14.8 ± 5.1** | 387.9 ± 25.4 | 67.3 ± 21.7 |

### Figures

**Fig 1 — Metric Distributions (30 runs)**  
Box plots showing statistical spread for all 8 metrics across all 3 protocols.

![Fig 1 – Box Plots](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig1_BoxPlots.png)

---

**Fig 2 — Distance Analysis (1–50 km)**  
How each metric degrades with increasing transmission distance, with ±1 SD confidence bands.

![Fig 2 – Distance Analysis](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig2_Distance_Analysis.png)

---

**Fig 3 — Normalised Performance Radar**  
Spider chart showing relative protocol strengths. Radially outward = better on each axis.

![Fig 3 – Radar Chart](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig3_Radar_Chart.png)

---

**Fig 4 — Key-Metric Dashboard**  
Grouped bar charts with individual run scatter for the four most decision-relevant metrics.

![Fig 4 – Dashboard](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig4_Dashboard.png)

---

**Fig 5 — Security vs. Performance Trade-off**  
QBER vs. Throughput scatter (diamonds = per-protocol mean). Captures the fundamental security–efficiency trade-off.

![Fig 5 – Security Performance](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig5_Security_Performance.png)

---

**Fig 6 — Performance Heatmap**  
Colour-coded comparison across all metrics. Green = best relative rank; red = worst.

![Fig 6 – Heatmap](QKD_Simulation/Advanced%20Protocol%20Set/plots/findings/Fig6_Heatmap.png)

---

### Key Takeaways

- **BB84** achieves the highest key rate (170 bits) and throughput (164 Kbits/s) with zero QBER, making it optimal for high-bandwidth, lower-security-requirement scenarios.
- **E91** provides a quantum-mechanical security guarantee via Bell inequality violation (S ≈ 2.6 > 2), but suffers high channel loss (72%) because both entangled photons must survive transmission simultaneously.
- **MDI-QKD** is the most attack-resistant (eliminates all detector side-channel vulnerabilities), but incurs a ~12× communication overhead compared to BB84 (593 vs 51 messages) and the lowest throughput (13.8 Kbits/s).
- All three protocols degrade predictably with distance; MDI-QKD degrades fastest due to its mid-point Bell-State Measurement node requirement.

---

## 🗂️ Repository Structure

```
qc_project/
├── README.md                          ← This file
├── 2603.01980v1 (1).pdf               ← Base paper (Doolittle & Cubeddu, 2026)
└── QKD_Simulation/
    ├── findings_results.py            ← Benchmarking script (generates all figures)
    ├── Basic Protocol Set/            ← Self-contained Python implementations
    │   ├── bb84.py                    ← BB84 simulation
    │   ├── e91.py                     ← E91 simulation
    │   └── mdi.py                     ← MDI-QKD simulation
    ├── Advanced Protocol Set/         ← NetSquid-based modular implementations
    │   ├── run_protocols.py           ← Protocol runner & per-protocol plots
    │   ├── BB84/
    │   │   ├── BB84_main.py
    │   │   └── performance.py
    │   ├── E91/
    │   │   ├── E91_main.py
    │   │   ├── E91_Alice.py
    │   │   ├── E91_Bob.py
    │   │   ├── functions.py
    │   │   └── performance.py
    │   ├── MDI-QKD/
    │   │   ├── main.py
    │   │   ├── MDI_Alice.py
    │   │   ├── MDI_Bob.py
    │   │   ├── MDI_Charlie.py
    │   │   └── performance.py
    │   └── plots/
    │       ├── findings/              ← Comparative benchmark figures (Figs 1–6)
    │       └── *.png                  ← Per-protocol MDI-QKD plots
    └── venv/                          ← Python virtual environment
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Linux/macOS (NetSquid is not supported on Windows)
- A free [NetSquid account](https://netsquid.org/) for the Advanced Set (Basic Set has no external dependencies)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/qc_project.git
cd qc_project/QKD_Simulation
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
# Core dependencies (Basic Set)
pip install numpy matplotlib seaborn scipy

# NetSquid (Advanced Set) — requires free registration at netsquid.org
pip install netsquid
```

---

## 🚀 Usage

All commands are run from inside `QKD_Simulation/` with the venv active.

### Run the full benchmark (generates all 6 figures)

```bash
python findings_results.py
```

Runs 30 simulations per protocol at 10 km + a 6-point distance sweep (1–50 km).  
Output figures → `Advanced Protocol Set/plots/findings/`

### Run a single protocol (Basic Set)

```bash
python "Basic Protocol Set/bb84.py"
python "Basic Protocol Set/e91.py"
python "Basic Protocol Set/mdi.py"
```

### Run a single protocol (Advanced Set — requires NetSquid)

```bash
cd "Advanced Protocol Set"
python BB84/BB84_main.py
python E91/E91_main.py
python MDI-QKD/main.py
```

### Run the Advanced Set comparison runner

```bash
cd "Advanced Protocol Set"
python run_protocols.py
# Select: 1 (BB84), 2 (E91), 3 (MDI-QKD), or 4 (All)
```

---

## 📐 Performance Metrics

| Metric | Definition | Better |
|--------|-----------|--------|
| **Raw Key Rate** | Sifted key bits after basis reconciliation | ↑ Higher |
| **QBER** | Quantum Bit Error Rate — fraction of key bits in error | ↓ Lower |
| **Latency** | Total wall-clock time for key generation | ↓ Lower |
| **Channel Loss Rate** | Fraction of photons lost in transmission | ↓ Lower |
| **Throughput** | Final secure key bits per second | ↑ Higher |
| **Communication Overhead** | Classical messages exchanged during protocol | ↓ Lower |
| **Synchronization Time** | Time to align Alice and Bob's measurement bases | ↓ Lower |
| **Computation Time/Round** | Per-round processing time | ↓ Lower |

---

## 🔧 Physical Channel Models

| Model | Parameter | Value |
|-------|-----------|-------|
| Fibre Loss | `p_loss_length` | 0.2 dB/km |
| Fibre Loss (init) | `p_loss_init` | 0.1 dB |
| Depolarisation noise | `depolar_rate` | 0.008 (0.8%) |
| Speed of light in fibre | `c` | 1.9 × 10⁵ km/s |
| Detector efficiency | — | 85% |
| MDI BSM success rate | — | distance-dependent |
| E91 entanglement fidelity | — | 92% |

---

## 📚 References

1. Doolittle, B., & Cubeddu, M. (2026). *Quantum Network Simulation and Emulation: A Roadmap for Quantum Internet Design*. arXiv:2603.01980v1.

2. Bennett, C. H., & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing*. Proceedings of IEEE International Conference on Computers, Systems and Signal Processing.

3. Ekert, A. K. (1991). *Quantum cryptography based on Bell's theorem*. Physical Review Letters, 67(6), 661–663.

4. Lo, H.-K., Curty, M., & Qi, B. (2012). *Measurement-device-independent quantum key distribution*. Physical Review Letters, 108(13), 130503. arXiv:1109.1473.

5. Coopmans, T., et al. (2021). *NetSquid, a NETwork Simulator for QUantum Information using Discrete events*. Communications Physics, 4, 164.

---

## 📜 License

This project is licensed under the **MIT License** — see [QKD_Simulation/LICENSE](QKD_Simulation/LICENSE) for details.
