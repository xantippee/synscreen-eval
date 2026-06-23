# Capstone Video Presentation Script & Demo Outline
### Project: BioGuard-Eval (DNA Synthesis Screening & Adversarial Evals)
**Target Length:** 5 Minutes (Strict Limit)  
**Target Audience:** Google Judges (Technical & Safety Evaluators) + Broader Public (Social Media/LinkedIn)
**Presenter:** Linda Polfus, PhD

---

## ⏱️ Video Storyboard & Timing Outline

| Section | Timing | Visual on Screen | Key Focus |
|---|---|---|---|
| **1. The Hook** | 0:00 - 0:45 (45s) | Speaker on camera (or split screen with DNA/AI graphics) | Personal story (laid off), passion for biosecurity, and the problem. |
| **2. Why Agents?** | 0:45 - 1:30 (45s) | Architecture diagram (Defense vs. Attack Agent loop) | Explain the biological threats (codon optimization) and why static filters fail, requiring agents. |
| **3. The Architecture** | 1:30 - 2:15 (45s) | Code walkthrough in VS Code (`multi_agent_system.py`, `screener.py`) | Briefly explain the 3-tiered screener (exact, alignment, Random Forest classifier) and MCP server. |
| **4. The Demo** | 2:15 - 3:45 (90s) | Screen recording of Streamlit Web Dashboard | Paste presets, run synonymous codon optimization attacks, show Plotly evals. |
| **5. Developer Vibe & Build**| 3:45 - 4:30 (45s) | Running CLI tools in terminal or show code robustness | Talk about developer experience, self-healing code, and pure-Python zero-dependency implementation. |
| **6. Outro & Call to Action** | 4:30 - 5:00 (30s) | Speaker on camera | Inspiring conclusion, link to repo, call to share on social media. |

---

## 🎤 Rehearsal Script (Verbatim)

### 1. The Hook: Problem & Passion (0:00 - 0:45)
*(Camera: Close-up of you. Speak with passion and energy.)*

"Hi everyone! I’m Linda Polfus. Not long ago, I was laid off from my job as a computational biologist and genetic epidemiologist. It was tough, but I wanted to use this time to build something meaningful—something for the common good. 

Today, frontier AI models are revolutionizing biology, helping us design new medicines and vaccines. But there is a silent, dangerous dual-use risk. These same models can design biological threats or write blueprints for regulated toxins and viruses. 

To stop these threats from being physically printed in a lab, DNA synthesis providers screen orders against biological databases. But sophisticated threat actors can easily bypass standard database filters by modifying the sequence. 

I built **BioGuard-Eval**—a multi-agent adversarial framework and security safeguard to test, evaluate, and block these biosecurity threats before they leave the digital world."

---

### 2. Why Agents & The Genetics Problem (0:45 - 1:30)
*(Screen: Show the Multi-Agent Architecture diagram or slides explaining Codon Optimization.)*

"So, how do adversaries bypass biological screeners? 
1. First, there's **Codon Optimization**. Think of a protein sequence as a recipe: 'Bake a cake at 350 degrees.' Because the genetic code is redundant, an actor can rewrite the recipe using different words: 'Prepare the dessert in the oven heated to three-hundred and fifty degrees.' It creates the exact same toxin in the cell, but completely bypasses exact database matching.
2. They also use **Sequence Splitting**—like shipping an illegal safe in separate flat-pack boxes to assemble at home—and **Chimeric Insertion**, hiding the sequence inside a harmless plasmid vector like a Trojan Horse.

Why do we need agents here? Static security filters are static targets. To map the true safety boundaries of a biological guardrail, we need **dynamic, adaptive stress-testing**. 

BioGuard-Eval uses a **Multi-Agent System**. We have an `AttackAgent` that analyzes the screener's defenses and autonomously generates optimized codon-mutations, splits, and chimeric inserts. And we have a `DefenseAgent` representing the screener, which dynamically adapts parameters and thresholds to maintain a safe false-positive rate while catching the new attack vectors. They play a game-theoretic simulation to discover where our safeguards fail."

---

### 3. The Technical Build & Architecture (1:30 - 2:15)
*(Screen: Visual of VS Code showing `multi_agent_system.py` and `mcp_server.py`.)*

"To build this, I implemented three key concepts from the AI Coding Intensive course.

First, the **Multi-Agent System** using a custom Python framework. The Orchestrator manages the feedback loop, letting the Defense Agent adjust parameters when a bypass is detected, writing results to `multi_agent_report.md`.

Second, I built a custom **Model Context Protocol (MCP) Server** running over stdio. This server exposes the DNA screener, red-team agents, and adversarial generators as tools. Any coding assistant or LLM agent can connect to this server and screen genomic coordinates or code snippets in real-time *before* outputting them to a user.

Third, the **Security Features**. The screener uses a multi-tiered pipeline: exact matching, translated protein local alignment using the **Smith-Waterman algorithm** which I wrote from scratch in pure Python, and a **Random Forest Classifier** trained on TF-IDF amino acid k-mer frequencies."

---

### 4. Interactive Demo (2:15 - 3:45)
*(Screen: Open your browser to the Streamlit app at `http://localhost:8501`. Walk through the tabs.)*

"Let’s see the system in action!

Here is the **Sequence Screening Portal**. If I select a standard benign reporter like Green Fluorescent Protein, the system clears the order immediately. But if I load a **Regulated Glycoprotein Variant**, the screener flags the order as High Risk, showing exactly which Select Agent database was matched and identifying the pathogen family.

Now let’s look at the **Adversarial Evasion Lab**. This is where we test the bypasses. If I select a biological toxin and apply **Codon Optimization**, the system mutates the nucleotides. You can see the side-by-side DNA sequence alignment—the DNA similarity drops to 70%, but the translated amino acid sequences remain 100% identical. 

If we screen it under our default policies, you’ll see the exact matching database clears the order—but our protein local alignment and machine learning classifiers step in to block it!

If I switch to **Sequence Fragmentation**, splitting the DNA into 3 fragments, look at the screening table. The alignment scores drop below the safety threshold. But our Tier 3 Random Forest classifier catches it!

Finally, in the **System Evals** tab, we can visualize the aggregated performance of our agents across the testing dataset, charting the exact detection rates and false positive rates under different adversarial attacks using interactive Plotly charts."

---

### 5. Developer Vibe & Code Robustness (3:45 - 4:30)
*(Screen: Show the terminal running `python cli.py --multi-agent` or show the self-healing code in `app.py`.)*

"As a developer, I focused heavily on deployability and code robustness. 

The entire framework is implemented in pure, lightweight Python, compatible back to Python 3.5.2. I engineered **graceful degradation**—if the environment lacks scikit-learn, the screener switches automatically to local alignments instead of crashing. 

I also added a **self-healing loader** in the web dashboard. If there is a package version mismatch while loading the model pickle, the app catches it on page load, automatically deletes the mismatched files, and regenerates the trained model in the current environment context. 

We also have a fully featured **CLI tool** for running red-team leaderboards and simulations directly from the terminal."

---

### 6. Outro & Call to Action (4:30 - 5:00)
*(Camera: Close-up of you. Speak confidently and warm.)*

"AI is changing the world, and by building automated biological safeguards like **BioGuard-Eval**, we can ensure it is a force for good. 

I’m currently looking for new opportunities in computational biology, biosecurity, or ML engineering where I can apply these agentic safety skills. 

The entire project is open-source. The link to the repository is below. Please check out the code, share it on LinkedIn, and let’s build a safer future for AI and biology together. Thank you!"

---

## 💡 Pro-Tips for Recording the Video

1. **Be Enthusiastic:** Since you want social media exposure, your energy is key. Smile, speak clearly, and show genuine interest in the intersection of biology and AI safety.
2. **Use Zoom/Crop:** When recording the Streamlit dashboard, make sure your browser window is zoomed in (125% or 150%) so that the text and Plotly graphs are large, clear, and readable on phone screens.
3. **Smooth Transitions:** Practice moving between showing your face, showing the code in VS Code, and showing the Streamlit web browser. Keeping transitions smooth makes the video feel premium.
4. **Prepare the Terminal:** Before recording, run `python cli.py --multi-agent` once to ensure the data is cached, so that when you run it in the video, it executes instantly.
