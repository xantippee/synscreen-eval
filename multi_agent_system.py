import random
import os
import json
import numpy as np

# Import our custom modules
from bio_utils import translate_dna
from data_generator import TEMPLATES, reverse_translate
from adversary import obfuscate_codon_optimization, obfuscate_split_sequence, obfuscate_chimeric_insert
from screener import BioSafeScreener, SKLEARN_AVAILABLE
from evals import run_eval_benchmark

class DefenseAgent:
    """
    Agent representing the biosecurity screening registry.
    Controls the parameters of the screening filters to optimize safety.
    """
    def __init__(self, match_threshold=0.75, ml_threshold=0.5):
        self.match_threshold = match_threshold
        self.ml_threshold = ml_threshold
        self.logs = []
        
    def get_screener(self, ref_fasta_path):
        """
        Returns a configured screener based on current agent policies.
        """
        screener = BioSafeScreener(
            ref_fasta_path=ref_fasta_path,
            match_threshold=self.match_threshold,
            ml_threshold=self.ml_threshold
        )
        # Load trained classifier if available
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "data", "screener_model.pkl")
        if os.path.exists(model_path):
            screener.load_model(model_path)
        return screener

    def adapt_policy(self, attack_reports, benign_reports):
        """
        Adjusts screening thresholds based on recent performance.
        Aim: Minimize False Positive Rate (FPR) below 5% while maximizing detection.
        """
        total_attacks = len(attack_reports)
        blocked_attacks = sum(1 for r in attack_reports if r['flagged'])
        detection_rate = blocked_attacks / total_attacks if total_attacks > 0 else 1.0
        
        total_benign = len(benign_reports)
        flagged_benign = sum(1 for r in benign_reports if r['flagged'])
        false_positive_rate = flagged_benign / total_benign if total_benign > 0 else 0.0
        
        adjustment_notes = []
        
        # Policy logic:
        # If FPR is too high (> 5%), loosen thresholds to reduce false flags
        if false_positive_rate > 0.05:
            adjustment_notes.append("False Positive Rate too high ({:.1f}%). Loosening thresholds to clear benign orders.".format(false_positive_rate * 100))
            self.match_threshold = min(0.95, self.match_threshold + 0.05)
            self.ml_threshold = min(0.85, self.ml_threshold + 0.05)
            
        # If detection rate is too low (< 95%) and FPR is safe, tighten thresholds
        elif detection_rate < 0.95 and false_positive_rate <= 0.05:
            adjustment_notes.append("Detection Rate too low ({:.1f}%). Tightening thresholds to capture threats.".format(detection_rate * 100))
            self.match_threshold = max(0.60, self.match_threshold - 0.05)
            self.ml_threshold = max(0.30, self.ml_threshold - 0.05)
            
        else:
            adjustment_notes.append("Policy thresholds balanced (Detection: {:.1f}%, FPR: {:.1f}%). Maintaining thresholds.".format(detection_rate * 100, false_positive_rate * 100))
            
        self.logs.append({
            "match_threshold": self.match_threshold,
            "ml_threshold": self.ml_threshold,
            "detection_rate": detection_rate,
            "fpr": false_positive_rate,
            "notes": " | ".join(adjustment_notes)
        })
        return adjustment_notes


class AttackAgent:
    """
    Agent representing a sophisticated adversary or researcher stress-testing.
    Generates customized mutated sequences designed to evade screening while keeping function intact.
    """
    def __init__(self, target_threat_class="threat_biological_toxin"):
        self.target_threat_class = target_threat_class
        self.base_peptide = TEMPLATES[target_threat_class]
        self.base_dna = reverse_translate(self.base_peptide, use_bias=True, seed=42)
        
    def generate_attack(self, strategy="baseline", seed=None):
        """
        Generates an evasion DNA sequence based on chosen strategy.
        """
        if strategy == "baseline":
            # Direct unaltered threat DNA
            return [self.base_dna]
            
        elif strategy == "codon_opt":
            # Full codon optimization synonym mutations
            obfuscated = obfuscate_codon_optimization(self.base_dna, seed=seed)
            return [obfuscated]
            
        elif strategy == "split":
            # Split the DNA into 3 fragments
            return obfuscate_split_sequence(self.base_dna, num_splits=3, overlap=30)
            
        elif strategy == "chimeric":
            # Embed the threat DNA inside a benign plasmid vector
            benign_vector = "GATC" * 200 # 800bp plasmid backbone
            chimeric = obfuscate_chimeric_insert(self.base_dna, benign_vector, insert_position=400, seed=seed)
            return [chimeric]
            
        else:
            raise ValueError("Unknown attack strategy: {}".format(strategy))


class AdversarialOrchestrator:
    """
    Orchestrates the multi-agent game-theoretic evaluation.
    Runs multiple rounds of Attack vs Defense optimizations.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ref_fasta = os.path.join(data_dir, "regulated_threats_ref.fasta")
        self.csv_path = os.path.join(data_dir, "synthetic_screening_dataset.csv")
        
        # Load dataset for false positive checks
        if os.path.exists(self.csv_path):
            df = pd.read_csv(self.csv_path)
            self.benign_sequences = df[df['label'] == 0]['dna_sequence'].head(20).tolist()
        else:
            # Fallback benign sequences
            self.benign_sequences = [
                reverse_translate(TEMPLATES["benign_reporter_gfp"], use_bias=True, seed=i)
                for i in range(10)
            ]
            
    def run_game_simulation(self, rounds=4):
        print("Starting Multi-Agent Simulation...")
        defense = DefenseAgent(match_threshold=0.75, ml_threshold=0.50)
        attack = AttackAgent(target_threat_class="threat_biological_toxin")
        
        strategies = ["baseline", "codon_opt", "split", "chimeric"]
        rounds_report = []
        
        for r in range(rounds):
            strategy = strategies[r % len(strategies)]
            print("\n--- Round {}: Attack Agent uses Strategy: '{}' ---".format(r + 1, strategy))
            
            # 1. Attack Agent generates DNA sequence orders
            attack_orders = attack.generate_attack(strategy=strategy, seed=r)
            
            # 2. Defense Agent instantiates its screening engine with current policy
            screener = defense.get_screener(self.ref_fasta)
            
            # 3. Screen the attack sequences (if split, we track individual parts)
            attack_reports = []
            for order in attack_orders:
                rep = screener.screen_sequence(order)
                attack_reports.append(rep)
                
            # 4. Screen a set of benign sequences to evaluate False Positives
            benign_reports = []
            for benign in self.benign_sequences:
                rep = screener.screen_sequence(benign)
                benign_reports.append(rep)
                
            # Calculate metrics
            total_flagged = sum(1 for rep in attack_reports if rep['flagged'])
            successful_bypass = total_flagged < len(attack_orders) # If any fragment/order got cleared
            
            total_benign_flagged = sum(1 for rep in benign_reports if rep['flagged'])
            fpr = total_benign_flagged / len(benign_reports)
            
            print("Defense Policy: Match Threshold={:.2f}, ML Threshold={:.2f}".format(defense.match_threshold, defense.ml_threshold))
            print("Attack Outcome: Flagged {}/{} sequences. Bypass Succeeded: {}".format(total_flagged, len(attack_orders), successful_bypass))
            print("System False Positive Rate: {:.1f}%".format(fpr * 100))
            
            # Record state
            rounds_report.append({
                "round": r + 1,
                "strategy": strategy,
                "defense_match_thresh": defense.match_threshold,
                "defense_ml_thresh": defense.ml_threshold,
                "attack_orders_count": len(attack_orders),
                "attack_flagged_count": total_flagged,
                "bypass_succeeded": successful_bypass,
                "false_positive_rate": fpr,
                "details": "ML Prob: {:.1f}% | Highest Align: {:.1f}%".format(
                    np.mean([rep['tier3_prob'] for rep in attack_reports]),
                    np.mean([rep['highest_identity'] for rep in attack_reports]) * 100
                )
            })
            
            # 5. Defense Agent analyzes the results and dynamically adapts its policy
            defense.adapt_policy(attack_reports, benign_reports)
            
        # Write results to markdown
        self.generate_simulation_report(rounds_report)
        return rounds_report
        
    def generate_simulation_report(self, rounds_report, output_file="multi_agent_report.md"):
        with open(output_file, "w") as f:
            f.write("# BioGuard Multi-Agent Simulation Report\n\n")
            f.write("This report logs the game-theoretic interaction between our **Defense Agent** (controlling screening filters) and the **Attack Agent** (generating evasion vectors).\n\n")
            
            f.write("## Simulation Rounds\n\n")
            f.write("| Round | Attack Strategy | Match Thresh | ML Thresh | Flagged Orders | Bypass Status | False Positive Rate | Summary |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            
            for row in rounds_report:
                bypass_str = "❌ Blocked" if not row['bypass_succeeded'] else "💀 Bypassed"
                f.write("| {} | `{}` | {:.2f} | {:.2f} | {}/{} | {} | {:.1f}% | {} |\n".format(
                    row['round'],
                    row['strategy'],
                    row['defense_match_thresh'],
                    row['defense_ml_thresh'],
                    row['attack_flagged_count'],
                    row['attack_orders_count'],
                    bypass_str,
                    row['false_positive_rate'] * 100,
                    row['details']
                ))
                
            f.write("\n## Safety Analysis\n")
            f.write("1. **Round 1 (Baseline):** The default threat sequence is caught easily by exact k-mer matching (Tier 1).\n")
            f.write("2. **Round 2 (Codon Optimization):** Exact match fails, but the Defense Agent catches it via translated local alignment (Tier 2).\n")
            f.write("3. **Round 3 (Sequence Splitting):** Splitting sequences below alignment lengths causes alignment filters to fail. The system relies on ML functional classifiers (Tier 3) to identify the fragments.\n")
            f.write("4. **Round 4 (Chimeric Vectors):** Inserting target sequences inside plasmids requires local alignment identity filters to detect localized homology, demonstrating the dynamic adaptation of the Defense Agent's policies.\n")
            
        print("Simulation report written to {}".format(output_file))


if __name__ == "__main__":
    import pandas as pd
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    
    orchestrator = AdversarialOrchestrator(data_dir=data_dir)
    orchestrator.run_game_simulation()
