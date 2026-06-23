# BioGuard-Eval 🧬
### DNA Synthesis Screening, Multi-Agent Adversarial Simulation, and MCP Server for AI Biosecurity Safeguards

**BioGuard-Eval** (also known as *SynScreen-Eval*) is a biological safety safeguard and automated adversarial evaluation framework. Built for the **Agent for Good** track of the AI Coding Intensive Capstone, it simulates a DNA synthesis screening pipeline (filtering biological threat agents) and utilizes autonomous agents to stress-test these filters against codon optimization, sequence splitting, and chimeric insertion bypasses.

This project showcases the intersection of **computational biology, machine learning, and AI agent safety (red-teaming)**.

---

## 🌟 Key Features

*   **Multi-Tiered Screening Engine (`screener.py`):**
    *   **Tier 1 (Exact Match):** Fast nucleotide $k$-mer matching ($k=18$) against control databases.
    *   **Tier 2 (Homology Local Alignment):** Pure-Python **Smith-Waterman algorithm** running local alignments on translated protein sequences to catch codon-optimized threats.
    *   **Tier 3 (ML Functional Classifier):** Extracting amino acid 3-mers via TF-IDF and classifying them using a **Random Forest classifier** to detect functional threat signatures under heavy mutation or fragmentation.
*   **Adversarial Obfuscation Simulator (`adversary.py`):**
    *   *Codon Optimization:* Synonym mutations maximizing DNA sequence divergence while maintaining 100% amino acid identity.
    *   *Sequence Fragmentation:* Splitting DNA into overlapping segments to bypass length-based filters.
    *   *Chimeric Insertion:* Embedding pathogen sequences inside benign plasmid vectors.
*   **Multi-Agent Adversarial System (`multi_agent_system.py`):**
    *   **`AttackAgent`:** Simulates a threat actor generating optimized sequence variations to bypass filters.
    *   **`DefenseAgent`:** Dynamically tunes screener thresholds (alignment scores, ML thresholds) to maintain a False Positive Rate $<5\%$ while maximizing detection.
    *   **`AdversarialOrchestrator`:** Moderates the iterative rounds and logs the security boundary (`multi_agent_report.md`).
*   **Model Context Protocol (MCP) Server (`mcp_server.py`):**
    *   Exposes screening and simulation tools as JSON-RPC 2.0 stdio tools, enabling client AI coding agents (like Cursor, Claude Desktop) to screen code and genomic outputs autonomously.
*   **Command Line Interface (`cli.py`):**
    *   Interactive terminal tools to screen sequences, run the Red-Team benchmark, or launch the multi-agent simulator.
*   **Streamlit Web App Dashboard (`app.py`):**
    *   Interactive screening portal, adversarial playground, and Plotly performance eval charts with built-in **self-healing** model regeneration.

---

## 📁 Repository Structure

```text
synscreen-eval/
├── README.md                 # Professional repository landing page
├── requirements.txt          # Python dependencies
├── capstone_writeup.md       # Full capstone project submission report
├── cli.py                    # Command-line interface for the agent system
├── bio_utils.py              # DNA translation, FASTA parser, Smith-Waterman alignment
├── data_generator.py         # Synthetic, safe pathogen/benign dataset generator
├── adversary.py              # Adversarial sequence obfuscation simulators
├── screener.py               # 3-Tiered DNA screening pipeline (Exact, Local Align, ML)
├── evals.py                  # Training, testing, and evaluation benchmark runner
<<<<<<< HEAD
├── red_team_agent.py         # Autonomous evaluation agent
├── agent_report.md           # Generated safety report
└── app.py                    # Interactive Streamlit application
=======
├── red_team_agent.py         # Autonomous Red-Team evaluation agent
├── multi_agent_system.py     # Game-theoretic Defense vs Attack Agent simulation
├── mcp_server.py             # stdio Model Context Protocol (MCP) tool server
├── run_app.bat               # Double-clickable Windows runner
└── app.py                    # Interactive Streamlit dashboard
>>>>>>> 3a8bdab (Update agents, README, add video script and capstone assets)
```

---

## 🛠️ Installation & Quick Start

### 1. Install Dependencies
Ensure you have Python 3.5+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard (Easiest)
If on Windows, you can simply **double-click the `run_app.bat` file** in your file explorer. Alternatively, execute:
```bash
streamlit run app.py
```
*Note: On first startup, the app will automatically generate mock datasets, train the Random Forest model, and compile evaluations.*

### 3. Run the CLI Tool
Examine sequence safety, run the Red-Team evaluator, or run the multi-agent simulation from the terminal:
```bash
# Screen a DNA sequence
python cli.py --screen ATGGGGGGGGTGTTTATTTTGGTTGCTTTGATTTTGCAATCGTTTGGACAAGATATTTTGGTTACATCG

# Run the Multi-Agent Defense vs Attack simulation
python cli.py --multi-agent

# Run the autonomous Red-Team Agent benchmark
python cli.py --red-team --seeds 5
```

---

## 🧬 Capstone Concepts Demonstrated

This project implements three key concepts covered in the course:

<<<<<<< HEAD
This framework stress-tests screening robustness using **automated capability evaluations (Evals)**, reporting performance metrics:

1. **Exact Match (Tier 1)** works perfectly against unmodified sequences, but drops to **0% detection** under codon optimization since the nucleotide sequence is changed.
2. **Homology Alignment (Tier 2)** detects codon-optimized threats but suffers a drop in detection if sequences are fragmented (Split Order Attack), as individual segments are too short to trigger length-based thresholds.
3. **ML Classifier (Tier 3)** provides redunancy, classifying the functional class of the sequence regardless of heavy mutations or fragmentation.

 ## 🤖 Autonomous BioGuard Red Team Agent

The repository includes a safe autonomous evaluation agent (red_team_agent.py) that repeatedly generates synthetic datasets, executes benchmark evaluations, analyzes outcomes, ranks performance, and produces structured reports.

**Agent Workflow:**

Generate synthetic biological test cases
Execute screening pipeline
Run benchmark evaluations
Analyze detection performance
Identify recurring failure modes
Generate leaderboard rankings
Produce reproducible safety reports

Unlike static benchmarks, the agent continuously evaluates screening robustness across multiple synthetic scenarios and highlights areas where detection performance may vary.

## 🚀 Running the Autonomous Agent

Execute the evaluation agent:

**python red_team_agent.py**

The agent will:

1. Generate synthetic evaluation datasets
2. Run multiple benchmark cycles
3. Compare detection performance
4. Produce leaderboard rankings
5. Generate agent_report.md

**Example output:**

Starting Safe Red-Team Agent

Running evaluation cycle: seed=0
...
Running evaluation cycle: seed=9

=== Safe Red-Team Leaderboard === 1. Seed=4 | Baseline=100% 2. Seed=7 | Baseline=100% Report written to agent_report.md Safe Red-Team Agent completed.

## 🔮 Future Work

### Adaptive Evaluation Agent

Extend the Red Team Agent to automatically identify the weakest-performing screening scenario from previous evaluation runs and prioritize future synthetic test generation in those areas. For example, if chimeric sequence detection consistently underperforms baseline detection, the agent would generate additional synthetic chimeric test cases and measure whether screening improvements close the gap.

### Detection Drift Monitoring

Track screening performance across successive model versions and benchmark runs. Generate longitudinal reports showing changes in detection rates, false positive rates, and performance on codon-variant, fragmented, and chimeric synthetic sequences.

### Functional Sequence Classification Analysis

Expand the machine learning component to compare alternative feature representations, including amino-acid k-mers, protein embeddings, and transformer-based sequence encoders, using the same synthetic evaluation framework.

### Automated Evaluation Reports

Generate publication-style evaluation summaries that automatically describe benchmark results, identify statistically significant performance changes, and summarize screening strengths and limitations across all test scenarios.

### Expanded Synthetic Benchmark Library

Develop a larger collection of safe synthetic benchmark datasets containing diverse sequence lengths, codon usage profiles, GC-content distributions, and engineered sequence architectures to improve evaluation coverage.

### Interactive Evaluation Dashboard

Extend the Streamlit application with trend analysis, run-to-run comparisons, benchmark history tracking, and visual exploration of detection performance across multiple evaluation cycles.

### Reproducible Screening Benchmark Suite

Package the framework as a reusable benchmark suite that allows researchers to compare screening approaches using standardized synthetic datasets, evaluation metrics, and reporting workflows.

=======
1.  **Agent & Multi-Agent Systems (ADK):** Exposes an adversarial game between a `DefenseAgent` (screener) and an `AttackAgent` (adversary). The agents negotiate thresholds dynamically, showcasing a structured reinforcement loop in `multi_agent_system.py`.
2.  **Model Context Protocol (MCP) Server:** Implements a JSON-RPC stdio protocol server (`mcp_server.py`) that allows external LLMs to invoke biological safety checks as tools during generation.
3.  **Security Features:** Implements a multi-tiered defense pipeline (local homology + ML classifier) with defensive engineering features like **graceful degradation** (if `scikit-learn` is missing, exact matching and local alignment remain operational) and **self-healing pickle loading** (re-compiling models on the fly in the event of package version mismatches).
>>>>>>> 3a8bdab (Update agents, README, add video script and capstone assets)
