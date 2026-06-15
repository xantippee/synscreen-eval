import random
# Import pure python utilities
from bio_utils import translate_dna
from data_generator import CODON_TABLE

def obfuscate_codon_optimization(dna_seq, seed=None):
    """
    Translates a DNA sequence to protein and reverse translates it using 
    random codons to maximize nucleotide sequence divergence while maintaining 
    the exact same translated protein sequence (synonymous mutation attack).
    """
    if seed is not None:
        random.seed(seed)
        
    protein_seq = translate_dna(dna_seq)
    
    obfuscated_codons = []
    for i, aa in enumerate(protein_seq):
        if aa not in CODON_TABLE:
            raise ValueError("Unknown amino acid character: {}".format(aa))
        
        # Get all codons for this amino acid
        all_codons = CODON_TABLE[aa]
        
        # Find the original codon used
        original_codon = dna_seq[i*3:(i+1)*3].upper()
        
        # Try to choose a codon different from the original to maximize mutation
        alternatives = [c for c in all_codons if c != original_codon]
        
        if alternatives:
            chosen_codon = random.choice(alternatives)
        else:
            chosen_codon = original_codon # If only one codon exists (e.g. Methionine ATG)
            
        obfuscated_codons.append(chosen_codon)
        
    return "".join(obfuscated_codons)

def obfuscate_split_sequence(dna_seq, num_splits=3, overlap=30):
    """
    Splits a DNA sequence into multiple overlapping segments (simulating split orders 
    that bypass length-based screening and are assembled in-lab using Gibson/Overlap Assembly).
    """
    seq_len = len(dna_seq)
    if num_splits <= 1:
        return [dna_seq]
        
    # Calculate base size of each fragment
    base_size = seq_len // num_splits
    fragments = []
    
    for i in range(num_splits):
        start = max(0, i * base_size - (overlap if i > 0 else 0))
        end = min(seq_len, (i + 1) * base_size + (overlap if i < num_splits - 1 else 0))
        
        # Adjust last fragment to cover the rest of the sequence
        if i == num_splits - 1:
            end = seq_len
            
        fragments.append(dna_seq[start:end])
        
    return fragments

def obfuscate_chimeric_insert(target_dna, carrier_dna, insert_position=None, seed=None):
    """
    Embeds the threat DNA sequence into a larger, benign carrier DNA sequence.
    This simulates inserting a pathogen gene into a standard expression vector or plasmid.
    """
    if seed is not None:
        random.seed(seed)
        
    carrier_len = len(carrier_dna)
    
    if insert_position is None:
        # Default insert in the middle of carrier DNA
        insert_position = carrier_len // 2
    else:
        insert_position = min(max(0, insert_position), carrier_len)
        
    left_flank = carrier_dna[:insert_position]
    right_flank = carrier_dna[insert_position:]
    
    # Return chimeric DNA
    return left_flank + target_dna + right_flank

if __name__ == "__main__":
    # Test functions
    test_dna = "ATGGGGGGGGTGTTTATTTTGGTTGCTTTGATTTTGCAATCGTTTGGACAAGATATTTTGGTTACATCG"
    print("Original DNA:   ", test_dna)
    print("Original AA:    ", translate_dna(test_dna))
    
    obf_codon = obfuscate_codon_optimization(test_dna, seed=42)
    print("Codon Obf DNA:  ", obf_codon)
    print("Codon Obf AA:   ", translate_dna(obf_codon))
    print("Divergent?      ", test_dna != obf_codon)
    
    splits = obfuscate_split_sequence(test_dna, num_splits=3, overlap=6)
    print("Splits:         ", splits)
    print("Split length:   ", [len(s) for s in splits])
    
    carrier = "C"*50
    chimeric = obfuscate_chimeric_insert(test_dna, carrier)
    print("Chimeric length:", len(chimeric))
