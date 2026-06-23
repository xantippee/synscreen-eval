# BioGuard-Eval 🧬
### DNA Synthesis Screening · Multi-Agent Adversarial Simulation · MCP Server for AI Biosecurity

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Coding Capstone](https://img.shields.io/badge/Google%20AI%20Coding-Capstone%202026-orange.svg)]()

**BioGuard-Eval** (also known as *SynScreen-Eval*) is a biological safety safeguard and automated adversarial evaluation framework. Built for the **Agent for Good** track of the AI Coding Intensive Capstone, it simulates a DNA synthesis screening pipeline — filtering biological threat agents — and deploys autonomous agents to stress-test these filters against codon optimization, sequence splitting, and chimeric insertion bypass techniques.

This project showcases the intersection of **computational biology, machine learning, and AI agent safety (red-teaming)** — all without using any real pathogen data.

---

## 🌟 Key Features

### 🔬 Multi-Tiered Screening Engine (`screener.py`)
- **Tier 1 — Exact Match:** Fast nucleotide *k*-mer matching (*k*=18) against regulated sequence databases.
- **Tier 2 — Homology Alignment:** Pure-Python **Smith-Waterman** local alignment on translated protein sequences to catch codon-optimized threats.
- **Tier 3 — ML Functional Classifier:** Amino acid 3-mer TF-IDF features classified by a **Random Forest** model to detect functional threat signatures under heavy mutation or fragmentation.

### 🎭 Adversarial Obfuscation Simulator (`adversary.py`)
- **Codon Optimization:** Synonym mutations maximizing DNA divergence while preserving 100% amino acid identity.
- **Sequence Fragmentation:** Splitting DNA into overlapping segments to bypass length-based filters.
- **Chimeric Insertion:** Embedding pathogen-mimicking segments inside benign plasmid vectors.

### 🤖 Multi-Agent Adversarial System (`multi_agent_system.py`)
- **`AttackAgent`:** Simulates a threat actor generating optimized sequence variations to bypass filters.
- **`DefenseAgent`:** Dynamically tunes screener thresholds (alignment scores, ML confidence) to maintain a False Positive Rate <5% while maximizing detection.
- **`AdversarialOrchestrator`:** Moderates iterative rounds and logs the evolving security boundary to `multi_agent_report.md`.

### 🛡️ Autonomous Red-Team Agent (`red_team_agent.py`)
- Autonomously generates synthetic test datasets, executes multi-seed benchmark cycles, analyzes detection failure modes, ranks screener performance, and produces structured safety reports (`agent_report.md`).

### 🔌 Model Context Protocol (MCP) Server (`mcp_server.py`)
- Exposes screening and simulation tools as **JSON-RPC 2.0 stdio tools**, enabling external LLM coding agents (Cursor, Claude Desktop, Gemini) to invoke biological safety checks autonomously during code generation.

### 💻 Command Line Interface (`cli.py`)
- Screen individual sequences, run the Red-Team benchmark, or launch the multi-agent simulation — all from the terminal.

### 📊 Streamlit Web App Dashboard (`app.py`)
- Interactive screening portal, adversarial playground, and Plotly performance evaluation charts with built-in **self-healing** model regeneration on version mismatch.

---

## 📁 Repository Structure

```text
synscreen-eval/
├── README.md               # You are here
├── requirements.txt        # Python dependencies
├── capstone_writeup.md     # Full capstone submission report (~2,500 words)
├── capstone_video_script.md# Video demo script and outline
├── run_app.bat             # Double-clickable Windows launcher
│
├── app.py                  # Streamlit interactive dashboard
├── cli.py                  # Command-line interface
├── bio_utils.py            # DNA translation, FASTA parser, Smith-Waterman alignment
├── data_generator.py       # Synthetic safe pathogen/benign dataset generator
├── adversary.py            # Adversarial sequence obfuscation simulators
├── screener.py             # 3-Tiered DNA screening pipeline
├── evals.py                # Training, testing, and benchmark runner
├── red_team_agent.py       # Autonomous Red-Team evaluation agent
├── multi_agent_system.py   # Game-theoretic Defense vs. Attack agent simulation
├── mcp_server.py           # stdio MCP tool server
└── data/                   # Auto-generated synthetic datasets (created on first run)
```

---

## 🛠️ Installation & Quick Start

### Prerequisites
- Python 3.7+ (tested on 3.9–3.11)
- `pip` package manager

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/synscreen-eval.git
cd synscreen-eval
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit Dashboard (Easiest)
On **Windows**, double-click `run_app.bat`. Or from any terminal:
```bash
streamlit run app.py
```
> **Note:** On first startup, the app automatically generates mock datasets, trains the Random Forest model, and compiles evaluations. No manual setup needed.

### 4. Use the CLI
```bash
# Screen a DNA sequence for threat content
python cli.py --screen ATGGGGGGGGTGTTTATTTTGGTTGCTTTGATTTTGCAATCGTTTGGACAAGATATTTTGGTTACATCG

# Run the multi-agent Defense vs. Attack simulation
python cli.py --multi-agent

# Run the autonomous Red-Team Agent benchmark
python cli.py --red-team --seeds 5
```

### 5. Run the Autonomous Red-Team Agent Directly
```bash
python red_team_agent.py
```
The agent will:
1. Generate synthetic evaluation datasets across multiple random seeds
2. Execute screening benchmarks across all three tiers
3. Compare detection performance under each adversarial attack type
4. Produce leaderboard rankings
5. Write a reproducible safety report to `agent_report.md`

**Example console output:**
```
Starting Safe Red-Team Agent
Running evaluation cycle: seed=0
...
Running evaluation cycle: seed=9

=== Safe Red-Team Leaderboard ===
1. Seed=4 | Tier 3 Accuracy=98.2% | Tier 1 Codon-Opt Detection=0%
2. Seed=7 | Tier 3 Accuracy=97.1% | Tier 1 Codon-Opt Detection=0%

Report written to agent_report.md
Safe Red-Team Agent completed.
```

---

## 🧬 Capstone Concepts Demonstrated

This project satisfies **≥ 3 key concepts** from the AI Coding Intensive Capstone:

| # | Concept | Where |
|---|---------|--------|
| 1 | **Agent & Multi-Agent Systems (ADK)** | `multi_agent_system.py`, `red_team_agent.py` |
| 2 | **Model Context Protocol (MCP) Server** | `mcp_server.py` |
| 3 | **Security Features** | `screener.py`, `adversary.py`, `evals.py` |
| 4 | **Agent Skills / CLI** | `cli.py` |
| 5 | **Deployability** | `run_app.bat`, `app.py` (Streamlit) |

### Concept Details

**1. Agent & Multi-Agent Systems**
`multi_agent_system.py` implements a game-theoretic loop between an `AttackAgent` (threat actor) and a `DefenseAgent` (screener). They negotiate thresholds dynamically across multiple rounds, showcasing structured adversarial reinforcement with an `AdversarialOrchestrator` mediating the interaction. The `red_team_agent.py` is a fully autonomous evaluation agent that requires no human input to run end-to-end benchmark cycles.

**2. Model Context Protocol (MCP) Server**
`mcp_server.py` implements the JSON-RPC 2.0 stdio protocol, exposing `screen_sequence`, `run_adversary`, and `run_eval` as callable tools. This allows any MCP-compatible AI assistant (Claude Desktop, Cursor, Gemini CLI) to autonomously invoke biological safety checks at generation time.

**3. Security Features**
The three-tiered screening pipeline provides **defense-in-depth**:
- Tier 1 catches unmodified threats instantly.
- Tier 2 catches codon-optimized evasion via protein-level alignment.
- Tier 3 catches fragmented or heavily mutated sequences via ML functional classification.
Additional engineering features include **graceful degradation** (exact matching and alignment remain operational if `scikit-learn` is unavailable) and **self-healing pickle loading** (models are automatically retrained on package version mismatch).

---

## 📈 How the Evaluation Works

The benchmark in `evals.py` stress-tests each screening tier against three adversarial attack types:

| Attack Type | Tier 1 (Exact) | Tier 2 (Alignment) | Tier 3 (ML) |
|-------------|---------------|-------------------|--------------|
| **Unmodified** | ✅ 100% | ✅ High | ✅ High |
| **Codon Optimized** | ❌ 0% | ✅ High | ✅ High |
| **Fragmented** | ❌ 0% | ⚠️ Partial | ✅ High |
| **Chimeric Insertion** | ❌ 0% | ⚠️ Partial | ✅ High |

This table demonstrates that **no single tier is sufficient** — the value of the multi-tiered, ML-backed approach is empirically validated by the automated evals themselves.

---

## ⚠️ Safety & Ethics Statement

All sequence data used in this project is **entirely synthetic and fictional**. No real pathogen sequences, select agent data, or export-controlled biological information is present in this repository. The project is designed strictly as an educational demonstration of AI safety evaluation methodology and biosecurity screening concepts.

This work aligns with responsible AI development principles and the dual-use research of concern (DURC) guidelines by focusing exclusively on **detection and defense** mechanisms.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Built as part of the **Google AI Coding Intensive Capstone 2026** — Agent for Good track.

> *Combining genetic epidemiology, machine learning, and AI agent safety to demonstrate responsible innovation at the intersection of biology and artificial intelligence.*
