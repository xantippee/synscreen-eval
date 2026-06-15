import os
import json
import random
import pandas as pd
import numpy as np

# Import modules from our project
from bio_utils import translate_dna
from adversary import obfuscate_codon_optimization, obfuscate_split_sequence, obfuscate_chimeric_insert
from screener import BioSafeScreener, SKLEARN_AVAILABLE

def run_eval_benchmark(data_dir=None, output_dir=None, seed=42):
    """
    Trains the screening pipeline and evaluates its performance on standard 
    and adversarial sequences (codon optimization, splitting, chimeras).
    Saves the benchmark results to evaluation_report.json.
    """
    if data_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "data")
    if output_dir is None:
        output_dir = data_dir
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Load dataset and reference
    csv_path = os.path.join(data_dir, "synthetic_screening_dataset.csv")
    ref_fasta_path = os.path.join(data_dir, "regulated_threats_ref.fasta")
    
    if not os.path.exists(csv_path) or not os.path.exists(ref_fasta_path):
        raise FileNotFoundError("Mock datasets not found. Please run data_generator.py first.")
        
    df = pd.read_csv(csv_path)
    
    # Manual Train/Test Split (70% Train, 30% Test) in pure Python (no sklearn dependency)
    random.seed(seed)
    indices = list(range(len(df)))
    random.shuffle(indices)
    split_idx = int(len(df) * 0.7)
    
    train_df = df.iloc[indices[:split_idx]].copy()
    test_df = df.iloc[indices[split_idx:]].copy()
    
    # Initialize screener
    screener = BioSafeScreener(ref_fasta_path=ref_fasta_path)
    
    # Train ML classifier only if scikit-learn is available
    if SKLEARN_AVAILABLE:
        screener.fit_ml_classifier(train_df)
        model_path = os.path.join(output_dir, "screener_model.pkl")
        screener.save_model(model_path)
    else:
        print("ML Model training skipped: scikit-learn not available.")
    
    print("\n--- Evaluating Test Set ---")
    
    benign_test = test_df[test_df['label'] == 0].copy()
    threat_test = test_df[test_df['label'] == 1].copy()
    
    print("Test set size: {} benign, {} threats".format(len(benign_test), len(threat_test)))
    
    # Pre-generate benign DNA string for chimeric insertion backbone
    vector_backbone = "GATC" * 200 # 800bp GC-balanced benign sequence
    
    results = {
        "summary": {},
        "detections": {
            "benign_baseline": [],
            "threat_baseline": [],
            "threat_codon_opt": [],
            "threat_split": [],
            "threat_chimeric": []
        }
    }
    
    # Helper to evaluate a list of DNA sequences
    def evaluate_sequences(dna_seqs, category_name):
        detections = []
        for dna in dna_seqs:
            report = screener.screen_sequence(dna)
            detections.append({
                "flagged": report['flagged'],
                "tier1_flag": report['tier1_flag'],
                "tier2_flag": report['tier2_flag'],
                "tier3_flag": report['tier3_flag'],
                "tier3_prob": report['tier3_prob'],
                "highest_identity": report['highest_identity']
            })
        return detections

    # 1. Benign Baseline
    print("Evaluating benign sequences...")
    results["detections"]["benign_baseline"] = evaluate_sequences(benign_test['dna_sequence'], "benign_baseline")
    
    # 2. Threat Baseline (unobfuscated)
    print("Evaluating baseline threat sequences...")
    results["detections"]["threat_baseline"] = evaluate_sequences(threat_test['dna_sequence'], "threat_baseline")
    
    # 3. Threat Codon Optimized
    print("Simulating and evaluating codon-optimized threats...")
    codon_opt_seqs = [obfuscate_codon_optimization(dna, seed=seed) for dna in threat_test['dna_sequence']]
    results["detections"]["threat_codon_opt"] = evaluate_sequences(codon_opt_seqs, "threat_codon_opt")
    
    # 4. Threat Split (evaluate if any of the fragments bypasses)
    print("Simulating and evaluating split sequence threats...")
    split_detections = []
    for dna in threat_test['dna_sequence']:
        fragments = obfuscate_split_sequence(dna, num_splits=3, overlap=30)
        frag_reports = [screener.screen_sequence(frag) for frag in fragments]
        
        # Aggregate: Was at least one fragment flagged?
        flagged = any(r['flagged'] for r in frag_reports)
        tier1_flag = any(r['tier1_flag'] for r in frag_reports)
        tier2_flag = any(r['tier2_flag'] for r in frag_reports)
        tier3_flag = any(r['tier3_flag'] for r in frag_reports)
        max_prob = max(r['tier3_prob'] for r in frag_reports)
        max_identity = max(r['highest_identity'] for r in frag_reports)
        
        split_detections.append({
            "flagged": flagged,
            "tier1_flag": tier1_flag,
            "tier2_flag": tier2_flag,
            "tier3_flag": tier3_flag,
            "tier3_prob": max_prob,
            "highest_identity": max_identity
        })
    results["detections"]["threat_split"] = split_detections
    
    # 5. Threat Chimeric Insertion
    print("Simulating and evaluating chimeric insertion threats...")
    chimeric_seqs = [obfuscate_chimeric_insert(dna, vector_backbone, seed=seed) for dna in threat_test['dna_sequence']]
    results["detections"]["threat_chimeric"] = evaluate_sequences(chimeric_seqs, "threat_chimeric")
    
    # Compute summary statistics
    def summarize_category(dets, is_threat=True):
        n = len(dets)
        if n == 0:
            return {}
        
        flagged_count = sum(1 for d in dets if d['flagged'])
        t1_count = sum(1 for d in dets if d['tier1_flag'])
        t2_count = sum(1 for d in dets if d['tier2_flag'])
        t3_count = sum(1 for d in dets if d['tier3_flag'])
        avg_identity = np.mean([d['highest_identity'] for d in dets])
        avg_ml_prob = np.mean([d['tier3_prob'] for d in dets])
        
        rate_name = "detection_rate" if is_threat else "false_positive_rate"
        
        return {
            "total_count": n,
            "flagged_count": flagged_count,
            rate_name: round(flagged_count / n, 4),
            "tier1_trigger_rate": round(t1_count / n, 4),
            "tier2_trigger_rate": round(t2_count / n, 4),
            "tier3_trigger_rate": round(t3_count / n, 4),
            "average_ref_identity": round(float(avg_identity), 4),
            "average_ml_probability": round(float(avg_ml_prob), 4)
        }

    results["summary"] = {
        "benign_baseline": summarize_category(results["detections"]["benign_baseline"], is_threat=False),
        "threat_baseline": summarize_category(results["detections"]["threat_baseline"], is_threat=True),
        "threat_codon_opt": summarize_category(results["detections"]["threat_codon_opt"], is_threat=True),
        "threat_split": summarize_category(results["detections"]["threat_split"], is_threat=True),
        "threat_chimeric": summarize_category(results["detections"]["threat_chimeric"], is_threat=True),
    }
    
    # Output to stdout
    print("\n--- BENCHMARK REPORT SUMMARY ---")
    print("Benign Baseline (False Positives): {:.2f}%".format(results["summary"]["benign_baseline"]["false_positive_rate"] * 100))
    print("Threat Baseline Detection:        {:.2f}%".format(results["summary"]["threat_baseline"]["detection_rate"] * 100))
    print("Threat Codon Opt Detection:        {:.2f}%".format(results["summary"]["threat_codon_opt"]["detection_rate"] * 100))
    print("Threat Split Detection:           {:.2f}%".format(results["summary"]["threat_split"]["detection_rate"] * 100))
    print("Threat Chimeric Detection:        {:.2f}%".format(results["summary"]["threat_chimeric"]["detection_rate"] * 100))
    
    # Save JSON report
    report_path = os.path.join(output_dir, "evaluation_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nSaved benchmark report to: {}".format(report_path))
    return results

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    run_eval_benchmark(data_dir=data_dir)
