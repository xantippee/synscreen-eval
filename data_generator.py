import random
import os
import pandas as pd
# Import our custom pure python utilities
from bio_utils import translate_dna, write_fasta

# Standard codon table (Standard Genetic Code)
CODON_TABLE = {
    'A': ['GCT', 'GCC', 'GCA', 'GCG'],
    'C': ['TGT', 'TGC'],
    'D': ['GAT', 'GAC'],
    'E': ['GAA', 'GAG'],
    'F': ['TTT', 'TTC'],
    'G': ['GGT', 'GGC', 'GGA', 'GGG'],
    'H': ['CAT', 'CAC'],
    'I': ['ATT', 'ATC', 'ATA'],
    'K': ['AAA', 'AAG'],
    'L': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
    'M': ['ATG'],
    'N': ['AAT', 'AAC'],
    'P': ['CCT', 'CCC', 'CCA', 'CCG'],
    'Q': ['CAA', 'CAG'],
    'R': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
    'S': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'],
    'T': ['ACT', 'ACC', 'ACA', 'ACG'],
    'V': ['GTT', 'GTC', 'GTA', 'GTG'],
    'W': ['TGG'],
    'Y': ['TAT', 'TAC'],
    '*': ['TAA', 'TAG', 'TGA']  # Stop codons
}

# Human codon usage frequencies (rough probabilities for realistic reverse translation)
HUMAN_CODON_BIAS = {
    'A': [0.26, 0.40, 0.23, 0.11],  # GCT, GCC, GCA, GCG
    'C': [0.46, 0.54],              # TGT, TGC
    'D': [0.46, 0.54],              # GAT, GAC
    'E': [0.42, 0.58],              # GAA, GAG
    'F': [0.45, 0.55],              # TTT, TTC
    'G': [0.16, 0.34, 0.25, 0.25],  # GGT, GGC, GGA, GGG
    'H': [0.42, 0.58],              # CAT, CAC
    'I': [0.36, 0.47, 0.17],        # ATT, ATC, ATA
    'K': [0.42, 0.58],              # AAA, AAG
    'L': [0.07, 0.13, 0.13, 0.26, 0.07, 0.34], # TTA, TTG, CTT, CTC, CTA, CTG
    'M': [1.0],                     # ATG
    'N': [0.46, 0.54],              # AAT, AAC
    'P': [0.28, 0.33, 0.28, 0.11],  # CCT, CCC, CCA, CCG
    'Q': [0.25, 0.75],              # CAA, CAG
    'R': [0.08, 0.19, 0.11, 0.20, 0.20, 0.22], # CGT, CGC, CGA, CGG, AGA, AGG
    'S': [0.15, 0.22, 0.15, 0.06, 0.15, 0.27], # TCT, TCC, TCA, TCG, AGT, AGC
    'T': [0.24, 0.36, 0.28, 0.12],  # ACT, ACC, ACA, ACG
    'V': [0.18, 0.24, 0.12, 0.46],  # GTT, GTC, GTA, GTG
    'W': [1.0],                     # TGG
    'Y': [0.43, 0.57],              # TAT, TAC
    '*': [0.28, 0.20, 0.52]         # TAA, TAG, TGA
}

# Mock base template sequences representing biological entities.
TEMPLATES = {
    # Simulates an Australia Group regulated viral glycoprotein (e.g. Ebola GP / Influenza HA homolog)
    "threat_viral_glycoprotein": (
        "MGGVFILVALILQSFGQDILVTSTLDGIRAVNDSLKTVTLSGLPLQLVDRVTGSSFLISG"
        "VTGLVTGTISGLYNLSSLSGVNPLSLASVGLPILSGLSGVNPLSLASGLPILSGLSGVNP"
        "LSLASVGLPILSVVTGLSSVVTGLSSVVTGLSSVVTGLSGIVNVTLSGLSGIVNVTLSGL"
        "SGLSSLSGVNPLSLASVGLPILSVVTGLSSLSGVNPLSLASVGLPILSVVTGLSSVVTGL"
        "SSLSGVNPLSLASVGLPILSVVTGLSSVVTGLSSVVTGLSSVVTGLSGIVNVTLSGLSGI"
        "YHNTSLQGVAQLPLSSLQDILVTSTLDGIRAVNDSLKTVTLSGLPLQLVDRVTGSSFLI*"
    ),
    # Simulates a regulated biological toxin (e.g. Ricin chain A homolog)
    "threat_biological_toxin": (
        "MFTLDASVATWMLVTFAVLVALVALASVAADAVTSLDGIRAVNDSLKTVTLSGLPLQLVD"
        "RVTGSSFLISGVTGLVTGTISGLYNLSSLSGVNPLSLASVGLPILSGLSGVNPLSLASGL"
        "PILSGLSGVNPLSLASVGLPILSVVTGLSSVVTGLSSVVTGLSSVVTGLSGIVNVTLSGL"
        "YHNTSLQGVAQLPLSSLQDILVTSTLDGIRAVNDSLKTVTLSGLPLQLVDRVTGSSFLIS"
        "GVTGLVTGTISGLYNLSSLSGVNPLSLASVGLPILSGLSGVNPLSLASGLPILSGLSGVN"
        "PLSLASVGLPILSVVTGLSSVVTGLSSVVTGLSSVVTGLSGIVNVTLSGLSGYHNTSLQ*"
    ),
    # Benign human housekeeping gene (e.g. Actin/GAPDH homolog)
    "benign_housekeeping": (
        "MDDDIAALVVDNGSGMCKAGFAGDDAPRAVFPSIVGRPRHQGVMVGMGQKDSYVGDEAQS"
        "KRGILTLKYPIEHGIITNWDDMEKIWHHTFYNELRVAPEEHPVLLTEAPLNPKANREKMT"
        "QIMFETFNTPAMYVAIQAVLSLYASGRTTGIVMDSGDGVTHTVPIYEGYALPHAILRLDL"
        "AGRDLTDYLMKILTERGYSFVTTAEREIVRDIKEKLCYVALDFEQEMATAASSSSLEKSY"
        "ELPDGQVITIGNERFRCPEALFQPSFLGMESCGIHETTFNSIMKCDVDIRKDLYANTVLS"
        "GGTTMYPGIADRMQKEITALAPSTMKIKIIAPPERKYSVWIGGSILASLSTFQQMWISK*"
    ),
    # Benign reporter protein (e.g. Green Fluorescent Protein GFP)
    "benign_reporter_gfp": (
        "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL"
        "VTTFTYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLV"
        "NRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLAD"
        "HYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK*"
    )
}

def weighted_choice(choices, weights, seed=None):
    """
    Selects a choice based on weights (compatible with Python 3.5).
    """
    if seed is not None:
        random.seed(seed)
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for c, w in zip(choices, weights):
        if upto + w >= r:
            return c
        upto += w
    return choices[-1]

def reverse_translate(protein_seq, use_bias=True, seed=None):
    """
    Reverse translates a protein sequence into a DNA sequence.
    If use_bias is True, uses human codon bias frequencies. Otherwise, selects uniformly.
    """
    if seed is not None:
        random.seed(seed)
        
    dna_seq_list = []
    for aa in protein_seq:
        if aa not in CODON_TABLE:
            raise ValueError("Unknown amino acid character: {}".format(aa))
        
        codons = CODON_TABLE[aa]
        if use_bias and aa in HUMAN_CODON_BIAS:
            weights = HUMAN_CODON_BIAS[aa]
            codon = weighted_choice(codons, weights)
        else:
            codon = random.choice(codons)
        dna_seq_list.append(codon)
        
    return "".join(dna_seq_list)

def mutate_protein_sequence(protein_seq, mutation_rate=0.05, seed=None):
    """
    Introduces random amino acid mutations (substitutions, insertions, deletions) into a protein sequence.
    This simulates natural variation or engineering.
    """
    if seed is not None:
        random.seed(seed)
        
    aa_list = list(CODON_TABLE.keys())
    if '*' in aa_list:
        aa_list.remove('*') # Avoid generating early stop codons mid-sequence
        
    mutated = []
    i = 0
    seq_len = len(protein_seq)
    
    # We leave the start codon (M) and stop codon (*) intact for valid translation
    mutated.append(protein_seq[0])
    
    for char in protein_seq[1:-1]:
        r = random.random()
        if r < mutation_rate:
            # Type of mutation: 85% substitution, 7.5% insertion, 7.5% deletion
            m_type = random.random()
            if m_type < 0.85:
                # Substitution
                mutated.append(random.choice(aa_list))
            elif m_type < 0.925:
                # Insertion (insert new amino acid + keep current)
                mutated.append(random.choice(aa_list))
                mutated.append(char)
            else:
                # Deletion (skip this character)
                continue
        else:
            mutated.append(char)
            
    mutated.append(protein_seq[-1])
    return "".join(mutated)

def generate_dataset(n_samples=200, output_dir="./data", seed=42):
    """
    Generates a mock dataset of DNA/Protein sequences with class labels.
    Divides them into:
      1. Reference Database (fasta format): Standard threats that the screener matches against.
      2. Train/Test dataset (csv format): Sequences for testing screening and ML classifiers.
    """
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    records = []
    ref_records = []
    
    # Generate reference database of threats
    # This acts as the "official list of select agents" that synthesis screening providers check against
    for label, peptide in TEMPLATES.items():
        if label.startswith("threat_"):
            # Create a reference record
            dna = reverse_translate(peptide, use_bias=True, seed=seed)
            ref_id = "REF_{}_001".format(label.upper())
            ref_records.append({
                "id": ref_id,
                "sequence": dna,
                "description": "Reference sequence for {}".format(label.replace('_', ' '))
            })
            
    # Save reference database to FASTA using our custom write_fasta function
    ref_fasta_path = os.path.join(output_dir, "regulated_threats_ref.fasta")
    write_fasta(ref_records, ref_fasta_path)
    print("Saved reference database of {} threat sequences to: {}".format(len(ref_records), ref_fasta_path))
    
    # Generate dataset (mix of threat and benign samples with mutations/variations)
    for i in range(n_samples):
        # Select template type
        template_name = random.choice(list(TEMPLATES.keys()))
        is_threat = 1 if template_name.startswith("threat_") else 0
        base_peptide = TEMPLATES[template_name]
        
        # Apply mutation to simulate natural variation or minor engineering (e.g. 3-8% mutation rate)
        mutation_rate = random.uniform(0.02, 0.08)
        mutated_peptide = mutate_protein_sequence(base_peptide, mutation_rate=mutation_rate)
        
        # Reverse translate with a randomized bias to simulate sequence engineering
        dna_seq = reverse_translate(mutated_peptide, use_bias=random.choice([True, False]))
        
        # Verify translation using our custom translate_dna function
        translated_seq = translate_dna(dna_seq)
        
        records.append({
            "sequence_id": "SEQ_{:04d}".format(i),
            "label": is_threat,
            "class_name": template_name,
            "mutation_rate": round(mutation_rate, 4),
            "protein_sequence": translated_seq,
            "dna_sequence": dna_seq,
            "length_nt": len(dna_seq),
            "length_aa": len(translated_seq)
        })
        
    df = pd.DataFrame(records)
    dataset_path = os.path.join(output_dir, "synthetic_screening_dataset.csv")
    df.to_csv(dataset_path, index=False)
    print("Generated {} simulated screening samples. Saved to: {}".format(n_samples, dataset_path))
    
    return df

if __name__ == "__main__":
    # Work relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    generate_dataset(output_dir=data_dir)
