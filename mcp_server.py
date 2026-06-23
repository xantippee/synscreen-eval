import sys
import json
import os
import traceback

# Import our custom modules
from bio_utils import translate_dna
from adversary import obfuscate_codon_optimization, obfuscate_split_sequence, obfuscate_chimeric_insert
from screener import BioSafeScreener, SKLEARN_AVAILABLE
from data_generator import generate_dataset
from evals import run_eval_benchmark
from multi_agent_system import AdversarialOrchestrator

# Setup paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
REF_FASTA_PATH = os.path.join(DATA_DIR, "regulated_threats_ref.fasta")
MODEL_PATH = os.path.join(DATA_DIR, "screener_model.pkl")

# Initialize cached screener instance
_screener = None

def get_screener():
    global _screener
    if _screener is None:
        # Check if ref files exist, otherwise create them
        if not os.path.exists(REF_FASTA_PATH):
            os.makedirs(DATA_DIR, exist_ok=True)
            generate_dataset(output_dir=DATA_DIR)
            run_eval_benchmark(data_dir=DATA_DIR)
            
        _screener = BioSafeScreener(ref_fasta_path=REF_FASTA_PATH)
        if SKLEARN_AVAILABLE and os.path.exists(MODEL_PATH):
            _screener.load_model(MODEL_PATH)
    return _screener

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    # Handle initialization handshake
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "bioguard-mcp-server",
                    "version": "1.0.0"
                }
            },
            "id": req_id
        }
        
    # Handle notifications (e.g. client initialized notification)
    if method == "notifications/initialized":
        return None
        
    # List available tools
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "screen_dna_sequence",
                        "description": "Screens a DNA nucleotide sequence against biological control lists (exact match, protein alignment, and ML classifier) to detect pathogen threats.",
                        "inputSchema": {
                          "type": "object",
                          "properties": {
                            "dna_sequence": {
                              "type": "string",
                              "description": "The raw DNA sequence (A, C, G, T) to screen."
                            }
                          },
                          "required": ["dna_sequence"]
                        }
                    },
                    {
                        "name": "simulate_evasion_attack",
                        "description": "Simulates an adversarial attack designed to obfuscate a threat sequence and bypass screening filters.",
                        "inputSchema": {
                          "type": "object",
                          "properties": {
                            "dna_sequence": {
                              "type": "string",
                              "description": "The base DNA sequence to obfuscate."
                            },
                            "strategy": {
                              "type": "string",
                              "enum": ["codon_opt", "split", "chimeric"],
                              "description": "The attack method: 'codon_opt' (synonymous mutations), 'split' (overlapping fragments), or 'chimeric' (plasmid insertion)."
                            }
                          },
                          "required": ["dna_sequence", "strategy"]
                        }
                    },
                    {
                        "name": "run_red_team_eval",
                        "description": "Executes the red-team agent benchmark across multiple seeds, generating performance leaderboards and markdown reports.",
                        "inputSchema": {
                          "type": "object",
                          "properties": {}
                        }
                    },
                    {
                        "name": "run_multi_agent_simulation",
                        "description": "Runs the game-theoretic simulation of the Defense Agent adapting thresholds dynamically to match the Attack Agent's evasions.",
                        "inputSchema": {
                          "type": "object",
                          "properties": {}
                        }
                    }
                ]
            },
            "id": req_id
        }
        
    # Call standard tools
    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            result_content = ""
            
            if tool_name == "screen_dna_sequence":
                dna_seq = arguments.get("dna_sequence", "")
                screener = get_screener()
                report = screener.screen_sequence(dna_seq)
                result_content = json.dumps(report, indent=2)
                
            elif tool_name == "simulate_evasion_attack":
                dna_seq = arguments.get("dna_sequence", "")
                strategy = arguments.get("strategy", "codon_opt")
                
                if strategy == "codon_opt":
                    out = obfuscate_codon_optimization(dna_seq, seed=42)
                    result_content = "Codon Optimized DNA:\n" + out
                elif strategy == "split":
                    out_list = obfuscate_split_sequence(dna_seq, num_splits=3, overlap=30)
                    result_content = "DNA Split Fragments:\n" + "\n".join(["Frag {}: {}".format(idx+1, f) for idx, f in enumerate(out_list)])
                elif strategy == "chimeric":
                    vector = "GATC" * 200
                    out = obfuscate_chimeric_insert(dna_seq, vector, insert_position=400, seed=42)
                    result_content = "Chimeric Vector DNA:\n" + out
                else:
                    result_content = "Error: Unknown strategy: " + strategy
                    
            elif tool_name == "run_red_team_eval":
                generate_dataset(output_dir=DATA_DIR)
                report = run_eval_benchmark(data_dir=DATA_DIR)
                result_content = "Evaluation Benchmark Summary:\n" + json.dumps(report["summary"], indent=2)
                
            elif tool_name == "run_multi_agent_simulation":
                orchestrator = AdversarialOrchestrator(data_dir=DATA_DIR)
                report = orchestrator.run_game_simulation()
                result_content = "Multi-Agent Simulation Summary:\n" + json.dumps(report, indent=2)
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": "Method not found: {}".format(tool_name)
                    },
                    "id": req_id
                }
                
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_content
                        }
                    ]
                },
                "id": req_id
            }
            
        except Exception as e:
            tb = traceback.format_exc()
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error: {}\n{}".format(str(e), tb)
                },
                "id": req_id
            }
            
    # Default error response
    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found: {}".format(method)
            },
            "id": req_id
        }
    return None

def main():
    # Force stdin and stdout to use UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
    
    # Simple line-by-line reading for stdio communication
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        try:
            req = json.loads(line)
            res = handle_request(req)
            if res:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            # Output error report in JSON-RPC format
            err_res = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error: {}".format(str(e))
                },
                "id": None
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
