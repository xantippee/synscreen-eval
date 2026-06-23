import argparse
import sys
import os
import json

# Import custom modules
from bio_utils import translate_dna
from screener import BioSafeScreener
from data_generator import generate_dataset
from evals import run_eval_benchmark
from red_team_agent import SafeRedTeamAgent
from multi_agent_system import AdversarialOrchestrator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
REF_FASTA_PATH = os.path.join(DATA_DIR, "regulated_threats_ref.fasta")
MODEL_PATH = os.path.join(DATA_DIR, "screener_model.pkl")

def check_setup():
    """
    Ensures safe mock datasets and models exist locally.
    """
    if not os.path.exists(REF_FASTA_PATH) or not os.path.exists(MODEL_PATH):
        print("First-time setup: Generating synthetic datasets and training models...")
        os.makedirs(DATA_DIR, exist_ok=True)
        generate_dataset(output_dir=DATA_DIR)
        run_eval_benchmark(data_dir=DATA_DIR)

def main():
    parser = argparse.ArgumentParser(
        description="BioGuard-Eval CLI: Biosecurity DNA Screening & Adversarial Evals CLI Tool"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--screen", 
        type=str, 
        help="Paste a raw DNA sequence (A, C, G, T) to screen for biosecurity threat risks."
    )
    group.add_argument(
        "--red-team", 
        action="store_true", 
        help="Run the autonomous Red-Team Agent benchmark across multiple seeds."
    )
    group.add_argument(
        "--multi-agent", 
        action="store_true", 
        help="Simulate the game-theoretic interaction between the Defense Agent and Attack Agent."
    )
    
    parser.add_argument(
        "--seeds", 
        type=int, 
        default=5, 
        help="Number of evaluation seeds to test for the red-team agent (default: 5)."
    )
    
    args = parser.parse_args()
    
    # Run setup check
    check_setup()
    
    if args.screen:
        print("\n--- Screening DNA Sequence ---")
        seq = args.screen.strip().upper()
        screener = BioSafeScreener(ref_fasta_path=REF_FASTA_PATH)
        screener.load_model(MODEL_PATH)
        
        report = screener.screen_sequence(seq)
        
        if report['flagged']:
            print("🚨 SCREENING STATUS: FLAGGED (HIGH RISK)")
        else:
            print("✅ SCREENING STATUS: CLEARED (SAFE)")
            
        print("Length: {} nt | Translated Length: {} aa".format(report['query_length_nt'], report['query_length_aa']))
        print("Tier 1 Exact Match Flag: {}".format("Triggered" if report['tier1_flag'] else "Passed"))
        print("Tier 2 Homology Alignment: {:.1f}% Identity".format(report['highest_identity'] * 100))
        print("Tier 3 ML Probability: {:.1f}%".format(report['tier3_prob'] * 100))
        
        if report['best_match_ref_id']:
            print("Matched Ref ID: {}".format(report['best_match_ref_id']))
            print("Classification: {}".format(report['best_match_desc']))
        if report['ml_flag_reason']:
            print("ML Reason: {}".format(report['ml_flag_reason']))
            
    elif args.red_team:
        print("\n--- Running Autonomous Red-Team Agent (Seeds: 0-{}) ---".format(args.seeds - 1))
        agent = SafeRedTeamAgent(data_dir=DATA_DIR, seeds=range(args.seeds))
        agent.run()
        agent.print_leaderboard()
        agent.generate_markdown_report()
        
    elif args.multi_agent:
        print("\n--- Running Multi-Agent Defense vs Attack Simulation ---")
        orchestrator = AdversarialOrchestrator(data_dir=DATA_DIR)
        orchestrator.run_game_simulation()
        
if __name__ == "__main__":
    main()
