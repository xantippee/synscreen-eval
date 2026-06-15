# SynScreen-Eval 🧬
### DNA Synthesis Screening & Adversarial Evaluation Framework

**SynScreen-Eval** (also referred to as *BioGuard-Eval*) is a Python-based simulation of DNA synthesis screening and automated adversarial evaluations. It demonstrates how biosecurity safeguards screen gene orders to prevent the illicit synthesis of regulated pathogens/toxins, and evaluates the resilience of these screeners against sophisticated evasion tactics.

This project was built to showcase the intersection of **machine learning, bioinformatics, and biological safety safeguards (biosecurity)**.

---

## 🌟 Key Features

* **Multi-Tiered Screening Pipeline:**
  * **Tier 1 (Exact Match):** Fast k-mer search ($k=18$) screening DNA against threat databases.
  * **Tier 2 (Homology Local Alignment):** Translates query DNA to protein and runs the **Smith-Waterman algorithm** (written in pure Python) against threat targets to identify matches despite synonymous mutations.
  * **Tier 3 (ML Functional Classifier):** Tokenizes amino acid sequences into overlapping 3-mers, vectorizes them via TF-IDF, and classifies sequences using a **Random Forest classifier** to detect functional threat signatures.
* **Adversarial Obfuscation Simulator:**
  * **Codon Optimization:** Mutates codons to maximize nucleotide sequence divergence while maintaining 100% amino acid identity (synonymous mutations).
  * **Sequence Fragmentation:** Splits sequences into overlapping fragments to bypass length-based filters.
  * **Chimeric Insertion:** Inserts threat sequences inside standard expression plasmids or benign backbones.
* **Interactive Streamlit Web Dashboard:**
  * Upload and screen custom DNA sequences.
  * Run adversarial attacks in a live visual playground (side-by-side nucleotide comparisons with protein identity checks).
  * View system-wide performance reports and evaluation charts (Plotly).

---

## 📁 Repository Structure

```text
synscreen-eval/
├── README.md                 # Professional repository documentation
├── requirements.txt          # Python dependencies
├── bio_utils.py              # DNA translation, FASTA parser, Smith-Waterman alignment
├── data_generator.py         # Synthetic, safe pathogen/benign dataset generator
├── adversary.py              # Adversarial sequence obfuscation simulators
├── screener.py               # 3-Tiered DNA screening pipeline (Exact, Local Align, ML)
├── evals.py                  # Training, testing, and evaluation benchmark runner
└── app.py                    # Interactive Streamlit application
```

---

## 🛠️ Setup & Local Run Instructions

### 1. Install Dependencies
Make sure you have Python 3.5+ installed. Install the requirements:
```bash
pip install -r requirements.txt
```

### 2. Run the App
Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

> [!NOTE]
> **Autobuild:** On first launch, the application will automatically check if the mock sequence datasets and machine learning models are present. If missing, it will programmatically generate the safe training data, train the Random Forest classifier, run the evaluation benchmark, and render the dashboard.

---

## 📊 How the Evals Work

Biosecurity guidelines (such as the *Guidance for Providers of Synthetic Double-Stranded DNA*) require screening systems to identify select agents. However, adversaries try to bypass simple filters.

This framework stress-tests screening robustness using **automated capability evaluations (Evals)**, reporting performance metrics:

1. **Exact Match (Tier 1)** works perfectly against unmodified sequences, but drops to **0% detection** under codon optimization since the nucleotide sequence is changed.
2. **Homology Alignment (Tier 2)** detects codon-optimized threats but suffers a drop in detection if sequences are fragmented (Split Order Attack), as individual segments are too short to trigger length-based thresholds.
3. **ML Classifier (Tier 3)** provides redunancy, classifying the functional class of the sequence regardless of heavy mutations or fragmentation.
