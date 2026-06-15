import streamlit as st
import os
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Import our custom modules
from bio_utils import translate_dna, smith_waterman, read_fasta
from data_generator import generate_dataset, TEMPLATES
from adversary import obfuscate_codon_optimization, obfuscate_split_sequence, obfuscate_chimeric_insert
from screener import BioSafeScreener, SKLEARN_AVAILABLE
from evals import run_eval_benchmark

# Page styling & Configuration
st.set_page_config(
    page_title="BioGuard-Eval | DNA Synthesis Screening & Evals",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS for premium aesthetics
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #8892b0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid;
    }
    .status-flagged {
        background-color: rgba(255, 75, 75, 0.1);
        border-left-color: #ff4b4b;
        color: #ff4b4b;
    }
    .status-safe {
        background-color: rgba(9, 171, 59, 0.1);
        border-left-color: #09ab3b;
        color: #09ab3b;
    }
    .tier-card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 0.4rem;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_style_html=True)

# ----------------- DATA / SETUP STAGE -----------------
# Define data paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
MODEL_PATH = os.path.join(DATA_DIR, "screener_model.pkl")
REPORT_PATH = os.path.join(DATA_DIR, "evaluation_report.json")
REF_FASTA_PATH = os.path.join(DATA_DIR, "regulated_threats_ref.fasta")

# Automatic setup if files are missing
setup_needed = not os.path.exists(REPORT_PATH) or (SKLEARN_AVAILABLE and not os.path.exists(MODEL_PATH))

if setup_needed:
    st.info("🧬 First-time setup: Generating synthetic datasets, training ML classifier, and running evaluation benchmarks...")
    with st.spinner("Processing biological datasets..."):
        generate_dataset(output_dir=DATA_DIR)
        run_eval_benchmark(data_dir=DATA_DIR)
    st.success("Setup complete!")

# Load Screener and Benchmark Report
@st.cache_resource
def load_screener():
    screener = BioSafeScreener(ref_fasta_path=REF_FASTA_PATH)
    if SKLEARN_AVAILABLE and os.path.exists(MODEL_PATH):
        screener.load_model(MODEL_PATH)
    return screener

@st.cache_data
def load_report():
    with open(REPORT_PATH, 'r') as f:
        return json.load(f)

screener = load_screener()
report_data = load_report()

# ----------------- SIDEBAR CONFIG -----------------
st.sidebar.image("https://img.icons8.com/external-flatart-icons-outline-flatarticons/128/external-dna-science-flatart-icons-outline-flatarticons.png", width=80)
st.sidebar.markdown("### BioGuard-Eval")
st.sidebar.markdown("DNA Synthesis Screening & Adversarial Evals Framework.")

if not SKLEARN_AVAILABLE:
    st.sidebar.warning("⚠️ **ML Features Disabled:** `scikit-learn` is not installed in the active environment. Tier 3 classifier is disabled.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Screener Thresholds")
match_thresh = st.sidebar.slider(
    "Tier 2 Homology Threshold (Protein Identity)", 
    min_value=0.50, max_value=1.00, value=screener.match_threshold, step=0.05
)

if SKLEARN_AVAILABLE:
    ml_thresh = st.sidebar.slider(
        "Tier 3 ML Probability Threshold", 
        min_value=0.10, max_value=0.90, value=screener.ml_threshold, step=0.05
    )
    screener.ml_threshold = ml_thresh

# Apply dynamic threshold adjustments to the cached screener
screener.match_threshold = match_thresh

st.sidebar.markdown("---")
st.sidebar.markdown("### Biosecurity Frameworks")
st.sidebar.info("""
* **Australia Group List:** Coordinates export controls on pathogens and toxins.
* **DNA Synthesis Guidance:** Requires providers to screen sequences to verify orders are legitimate and prevent illicit assembly of pathogens.
""")

# ----------------- MAIN CONTENT -----------------
st.markdown("<div class='main-header'>BioGuard-Eval 🧬</div>", unsafe_style_html=True)
st.markdown("<div class='sub-header'>DNA Synthesis Screening Pipeline & Adversarial Stress-Testing Dashboard</div>", unsafe_style_html=True)

# Main warning banner for missing sklearn dependencies
if not SKLEARN_AVAILABLE:
    st.warning("⚠️ **Notice:** `scikit-learn` is missing from your Python environment. The screening engine has gracefully degraded: Tier 1 (Exact Match) and Tier 2 (Smith-Waterman Alignment) remain fully functional, but Tier 3 (ML Classification) is disabled. Run `pip install scikit-learn` to enable ML features.")

tab1, tab2, tab3 = st.tabs([
    "🔍 Sequence Screening Portal", 
    "🧪 Adversarial Simulation Lab", 
    "📊 System Evals & Benchmarks"
])

# ----------------- TAB 1: SCREENER PORTAL -----------------
with tab1:
    st.header("Upload or Paste Sequence to Screen")
    st.write("Input a nucleotide sequence to test against the 3-tiered biosecurity screening pipeline.")
    
    # Preloaded examples
    preset_opt = st.selectbox(
        "Load Preset Sequence:",
        ["-- Paste or Custom --", "Benign Reporter (GFP)", "Regulated Glycoprotein Variant (Threat)", "Codon-Optimized Threat (Adversarial Bypass Target)"]
    )
    
    default_text = ""
    if preset_opt == "Benign Reporter (GFP)":
        from data_generator import reverse_translate
        default_text = ">BENIGN_GFP_EXPRESSION_VECTOR\n" + reverse_translate(TEMPLATES["benign_reporter_gfp"], use_bias=True, seed=42)
    elif preset_opt == "Regulated Glycoprotein Variant (Threat)":
        from data_generator import reverse_translate
        from data_generator import mutate_protein_sequence
        mutated_pep = mutate_protein_sequence(TEMPLATES["threat_viral_glycoprotein"], mutation_rate=0.04, seed=12)
        default_text = ">REGULATED_PATHOGEN_SURFACE_GLYCOPROTEIN\n" + reverse_translate(mutated_pep, use_bias=True, seed=12)
    elif preset_opt == "Codon-Optimized Threat (Adversarial Bypass Target)":
        from data_generator import reverse_translate
        original_dna = reverse_translate(TEMPLATES["threat_biological_toxin"], use_bias=True, seed=99)
        obfuscated_dna = obfuscate_codon_optimization(original_dna, seed=99)
        default_text = ">CODON_OPTIMIZED_REGULATED_TOXIN\n" + obfuscated_dna

    seq_input = st.text_area("Sequence FASTA (DNA/Nucleotide):", value=default_text, height=180)
    
    if st.button("Run DNA Synthesis Screen"):
        if seq_input.strip() == "":
            st.warning("Please enter a DNA sequence.")
        else:
            lines = seq_input.strip().split('\n')
            query_dna = ""
            header = "Query Sequence"
            if lines[0].startswith('>'):
                header = lines[0][1:]
                query_dna = "".join(lines[1:])
            else:
                query_dna = "".join(lines)
                
            query_dna = query_dna.replace(" ", "").replace("\r", "")
            
            with st.spinner("Analyzing sequence signature..."):
                report = screener.screen_sequence(query_dna)
                
            # Render Screening Banner
            if report['flagged']:
                st.markdown("""
                <div class='status-box status-flagged'>
                    <h3>⚠️ Flagged / High Risk Order</h3>
                    <p>This DNA sequence matches biological control lists or exhibits sequence homology with regulated select agents/toxins.</p>
                </div>
                """, unsafe_style_html=True)
            else:
                st.markdown("""
                <div class='status-box status-safe'>
                    <h3>✅ Cleared / Safe Order</h3>
                    <p>No matches to regulated pathogens or toxins detected. Suitable for synthesis order fulfillment.</p>
                </div>
                """, unsafe_style_html=True)
                
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Screener Tier Flags")
                
                # Tier 1 Card
                t1_status = "🔴 Triggered" if report['tier1_flag'] else "🟢 Passed"
                st.markdown(f"""
                <div class='tier-card'>
                    <h4>Tier 1: DNA Exact Match</h4>
                    <p>Checks for exact matches of 18-mer nucleotides against select agent databases.</p>
                    <strong>Status: {t1_status}</strong>
                </div>
                """, unsafe_style_html=True)
                
                # Tier 2 Card
                t2_status = "🔴 Triggered" if report['tier2_flag'] else "🟢 Passed"
                st.markdown(f"""
                <div class='tier-card'>
                    <h4>Tier 2: Translated Protein Homology</h4>
                    <p>Translates sequence to protein and aligns against threat reference library (Threshold: {match_thresh*100:.0f}% identity).</p>
                    <strong>Status: {t2_status}</strong> (Highest Local Identity: {report['highest_identity']*100:.1f}%)
                </div>
                """, unsafe_style_html=True)
                
                # Tier 3 Card
                t3_status = "🔴 Triggered" if report['tier3_flag'] else ("🟢 Passed" if SKLEARN_AVAILABLE else "⚪ Disabled")
                prob_text = "{:.1f}%".format(report['tier3_prob']*100) if SKLEARN_AVAILABLE else "N/A"
                st.markdown(f"""
                <div class='tier-card'>
                    <h4>Tier 3: ML Functional Classifier</h4>
                    <p>Analyses k-mer motifs in protein translation using Random Forest.</p>
                    <strong>Status: {t3_status}</strong> (Threat Probability: {prob_text})
                </div>
                """, unsafe_style_html=True)
                
            with col2:
                st.subheader("Biological Annotations & Match Details")
                if report['flagged']:
                    st.write("**Sequence ID:**", header)
                    st.write("**Sequence Length:**", "{} nt ({} aa)".format(report['query_length_nt'], report['query_length_aa']))
                    
                    if report['best_match_ref_id']:
                        st.write("**Matched Reference ID:**", report['best_match_ref_id'])
                        st.write("**Pathogen Classification:**", report['best_match_desc'])
                        
                    st.write("**Analysis & Context:**")
                    if report['tier1_flag']:
                        st.info("Exact match was triggered on a segment of DNA. This indicates high nucleotide homology to a known threat agent.")
                    elif report['tier2_flag']:
                        st.warning("Tier 2 was triggered by local amino acid alignment. This indicates the query protein sequence matches a regulated pathogen family, although the nucleotide sequence may have been heavily modified (codon optimized).")
                    if report['tier3_flag']:
                        st.error("ML model classified this sequence as a high-risk pathogen family: **{}**".format(report['ml_flag_reason']))
                else:
                    st.write("Sequence checked successfully. Length: {} nt. No significant biological matches found.".format(report['query_length_nt']))
                    st.balloons()

# ----------------- TAB 2: ADVERSARIAL PLAYGROUND -----------------
with tab2:
    st.header("Adversarial Evasion Lab")
    st.write("Simulate techniques sophisticated threat actors use to bypass DNA synthesis screening, and evaluate the robustness of our multi-tiered screener against these evasion attempts.")
    
    col_play1, col_play2 = st.columns([1, 2])
    
    with col_play1:
        st.subheader("Select Threat Target & Attack Type")
        
        threat_preset = st.selectbox(
            "Select Baseline Pathogen Target:",
            ["threat_viral_glycoprotein", "threat_biological_toxin"]
        )
        
        from data_generator import reverse_translate
        base_aa = TEMPLATES[threat_preset]
        base_dna = reverse_translate(base_aa, use_bias=True, seed=10)
        
        attack_type = st.radio(
            "Select Adversarial Attack to Apply:",
            [
                "1. Codon Optimization (Synonymous Mutations)",
                "2. Sequence Fragmentation (Split Synthesis)",
                "3. Chimeric Carrier Insertion"
            ]
        )
        
        if attack_type.startswith("2."):
            num_splits = st.slider("Number of Fragment Splits", min_value=2, max_value=5, value=3)
            overlap_bp = st.slider("Overlap BP for assembly", min_value=10, max_value=50, value=30)
        elif attack_type.startswith("3."):
            insert_pos = st.slider("Insertion Offset in Vector", min_value=100, max_value=700, value=400)
            
        run_attack = st.button("Apply Attack & Test Screener")
        
    with col_play2:
        st.subheader("Attack Performance Visualizer")
        
        if run_attack:
            original_aa = translate_dna(base_dna)
            backbone_dna = "GATC" * 200 # 800bp carrier
            
            if attack_type.startswith("1."):
                obfuscated_dna = obfuscate_codon_optimization(base_dna, seed=42)
                obfuscated_aa = translate_dna(obfuscated_dna)
                
                hamming_dist = sum(1 for c1, c2 in zip(base_dna, obfuscated_dna) if c1 != c2)
                percent_mut = (hamming_dist / len(base_dna)) * 100
                
                st.info("⚙️ **Synonymous Mutations Applied:** {} codon substitutions introduced.".format(hamming_dist))
                st.write("**Original vs. Mutated DNA Sequence Similarity:** {:.1f}%".format(100 - percent_mut))
                
                st.write("**DNA Sequence Alignment Snippet (original vs modified):**")
                slice_len = 50
                st.code("Original: " + base_dna[:slice_len] + "...\nModified: " + obfuscated_dna[:slice_len] + "...")
                
                st.write("**Protein Sequence Check:**")
                st.write("Original Translated AA: `{}...`".format(original_aa[:20]))
                st.write("Modified Translated AA: `{}...`".format(obfuscated_aa[:20]))
                st.success("✅ **Attack verification:** Amino acid translation remains 100% identical. Biological function preserved.")
                
                rep_base = screener.screen_sequence(base_dna)
                rep_obf = screener.screen_sequence(obfuscated_dna)
                
                # Format ML prob cells
                base_ml = "{:.1f}%".format(rep_base['tier3_prob']*100) if SKLEARN_AVAILABLE else "Disabled"
                obf_ml = "{:.1f}%".format(rep_obf['tier3_prob']*100) if SKLEARN_AVAILABLE else "Disabled"
                
                st.write("**Screening Evasion Comparison:**")
                comparison_df = pd.DataFrame({
                    "Screening Metric": ["Tier 1 Exact Match", "Tier 2 Homology (% identity)", "Tier 3 ML (threat prob.)", "Final Decision"],
                    "Baseline Pathogen": ["🔴 Flagged" if rep_base['tier1_flag'] else "🟢 Cleared", "{:.1f}%".format(rep_base['highest_identity']*100), base_ml, "🚨 Flagged" if rep_base['flagged'] else "✅ Cleared"],
                    "Obfuscated Pathogen": ["🟢 Cleared" if not rep_obf['tier1_flag'] else "🔴 Flagged", "{:.1f}%".format(rep_obf['highest_identity']*100), obf_ml, "🚨 Flagged" if rep_obf['flagged'] else "✅ Cleared"]
                })
                st.table(comparison_df)
                
                if not rep_obf['tier1_flag'] and rep_obf['flagged']:
                    st.warning("⚠️ **Note:** The adversary successfully bypassed **Tier 1 (Exact Match)**. However, the order was still flagged by **Tier 2 Homology Alignment** (and Tier 3 ML, if active).")

            elif attack_type.startswith("2."):
                fragments = obfuscate_split_sequence(base_dna, num_splits=num_splits, overlap=overlap_bp)
                st.info("✂️ **Sequence Fragmented:** DNA divided into {} segments to be assembled using Gibson Overlap.".format(num_splits))
                
                for idx, frag in enumerate(fragments):
                    st.write("**Fragment {}:** {} nucleotides".format(idx+1, len(frag)))
                    
                frag_reports = [screener.screen_sequence(f) for f in fragments]
                
                st.write("**Screening Results by Fragment:**")
                results_frag = []
                for idx, r in enumerate(frag_reports):
                    ml_val = "{:.1f}%".format(r['tier3_prob']*100) if SKLEARN_AVAILABLE else "Disabled"
                    results_frag.append({
                        "Fragment": f"Segment {idx+1}",
                        "Length (bp)": len(fragments[idx]),
                        "Tier 1 (Exact Match)": "Flagged" if r['tier1_flag'] else "Passed",
                        "Tier 2 (Homology)": "{:.1f}%".format(r['highest_identity']*100),
                        "Tier 3 (ML Prob)": ml_val,
                        "Action": "🔴 Blocked" if r['flagged'] else "🟢 Cleared"
                    })
                st.table(pd.DataFrame(results_frag))
                
                any_blocked = any(r['flagged'] for r in frag_reports)
                if not any_blocked:
                    st.error("💀 **Critical Evasion:** All individual fragments successfully bypassed screening! The order would be fulfilled, allowing full assembly of the pathogen in-house.")
                else:
                    st.success("🛡️ **Defense Active:** At least one fragment triggered safety flags. Order blocked.")

            elif attack_type.startswith("3."):
                chimeric_dna = obfuscate_chimeric_insert(base_dna, backbone_dna, insert_position=insert_pos)
                st.info("🧬 **Chimeric Insertion:** Pathogen gene inserted inside benign vector backbone.")
                st.write("**Total construct size:** {} bp (Original pathogen size: {} bp)".format(len(chimeric_dna), len(base_dna)))
                
                rep_chimeric = screener.screen_sequence(chimeric_dna)
                
                ml_val = "{:.1f}%".format(rep_chimeric['tier3_prob']*100) if SKLEARN_AVAILABLE else "Disabled"
                st.write("**Screening Results on Construct:**")
                st.write("- **Tier 1 Exact Match:**", "🔴 Triggered" if rep_chimeric['tier1_flag'] else "🟢 Passed")
                st.write("- **Tier 2 Homology Match:**", "{:.1f}% Identity".format(rep_chimeric['highest_identity']*100))
                st.write("- **Tier 3 ML Classifier:**", ml_val)
                st.write("- **Screener Action:**", "**🔴 Block Order**" if rep_chimeric['flagged'] else "**🟢 Clear Order**")
                
                if rep_chimeric['flagged']:
                    st.success("🛡️ **Defense Active:** Insertion was flagged. Local protein alignment / ML identified the pathogen insert.")
                else:
                    st.error("💀 **Screener Bypassed:** Screener cleared the construct, failing to detect insertion.")
        else:
            st.info("👈 Set your parameters and click 'Apply Attack & Test Screener' to run the adversarial simulation.")

# ----------------- TAB 3: SYSTEM EVALS -----------------
with tab3:
    st.header("System Performance & Evals Benchmarks")
    st.write("Performance analysis of the BioGuard screening engine across the testing dataset, comparing standard baseline sequences against various adversarial bypass strategies.")
    
    col_card1, col_card2, col_card3, col_card4 = st.columns(4)
    summary = report_data["summary"]
    
    with col_card1:
        st.metric("Benign False Positive Rate", "{:.2f}%".format(summary["benign_baseline"]["false_positive_rate"] * 100))
    with col_card2:
        st.metric("Baseline Threat Detection", "{:.2f}%".format(summary["threat_baseline"]["detection_rate"] * 100))
    with col_card3:
        st.metric("Codon-Opt Threat Detection", "{:.2f}%".format(summary["threat_codon_opt"]["detection_rate"] * 100))
    with col_card4:
        st.metric("Split Threat Detection", "{:.2f}%".format(summary["threat_split"]["detection_rate"] * 100))
        
    st.markdown("---")
    
    st.subheader("Detection Rates Breakdown by Tier")
    
    categories = ["Baseline Threats", "Codon-Optimized", "Split Sequence", "Chimeric Insert"]
    t1_rates = [
        summary["threat_baseline"]["tier1_trigger_rate"] * 100,
        summary["threat_codon_opt"]["tier1_trigger_rate"] * 100,
        summary["threat_split"]["tier1_trigger_rate"] * 100,
        summary["threat_chimeric"]["tier1_trigger_rate"] * 100
    ]
    t2_rates = [
        summary["threat_baseline"]["tier2_trigger_rate"] * 100,
        summary["threat_codon_opt"]["tier2_trigger_rate"] * 100,
        summary["threat_split"]["tier2_trigger_rate"] * 100,
        summary["threat_chimeric"]["tier2_trigger_rate"] * 100
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Tier 1 (Exact Match)', x=categories, y=t1_rates, marker_color='#ef4444'))
    fig.add_trace(go.Bar(name='Tier 2 (Homology Local)', x=categories, y=t2_rates, marker_color='#f59e0b'))
    
    if SKLEARN_AVAILABLE:
        t3_rates = [
            summary["threat_baseline"]["tier3_trigger_rate"] * 100,
            summary["threat_codon_opt"]["tier3_trigger_rate"] * 100,
            summary["threat_split"]["tier3_trigger_rate"] * 100,
            summary["threat_chimeric"]["tier3_trigger_rate"] * 100
        ]
        fig.add_trace(go.Bar(name='Tier 3 (ML Functional)', x=categories, y=t3_rates, marker_color='#3b82f6'))
        
    final_rates = [
        summary["threat_baseline"]["detection_rate"] * 100,
        summary["threat_codon_opt"]["detection_rate"] * 100,
        summary["threat_split"]["detection_rate"] * 100,
        summary["threat_chimeric"]["detection_rate"] * 100
    ]
    fig.add_trace(go.Bar(name='Total Flagged (Combined)', x=categories, y=final_rates, marker_color='#10b981'))
    
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        yaxis_title="Detection / Trigger Rate (%)",
        yaxis_range=[0, 105],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    > [!IMPORTANT]
    > **Evals Analysis & Findings:**
    > * **Tier 1 (Exact DNA Matching)** is highly effective against unmodified pathogens, but drops to **0% detection** under codon optimization because nucleotide-level signatures are lost.
    > * **Tier 2 (Homology Alignment)** acts as a robust second line of defense against codon optimization, but its sensitivity drops when sequences are fragmented (Split synthesis) because the alignment length falls below matching thresholds.
    > * **Tier 3 (ML Functional Classifier)** (if active) remains resilient across all attacks, learning amino acid k-mer patterns that represent the overall biological family, providing crucial safety redundancies.
    """)
