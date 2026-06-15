# Pure Python Utilities for Genomics and Sequence Alignment
# Eliminates external BioPython dependencies, making the project highly portable.

CODON_MAP = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
}

def translate_dna(dna_seq):
    """
    Translates a DNA sequence into a protein sequence.
    """
    dna_seq = dna_seq.upper().strip()
    protein = []
    for i in range(0, len(dna_seq) - 2, 3):
        codon = dna_seq[i:i+3]
        if len(codon) == 3:
            aa = CODON_MAP.get(codon, 'X')
            protein.append(aa)
    return "".join(protein)

def read_fasta(file_path):
    """
    Reads a FASTA file and returns a list of dictionaries with 'id', 'description', and 'sequence'.
    """
    records = []
    current_id = None
    current_desc = ""
    current_seq = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                if current_id is not None:
                    records.append({
                        'id': current_id,
                        'description': current_desc,
                        'sequence': "".join(current_seq)
                    })
                # Parse header
                header = line[1:]
                parts = header.split(None, 1)
                current_id = parts[0]
                current_desc = parts[1] if len(parts) > 1 else ""
                current_seq = []
            else:
                current_seq.append(line)
                
        if current_id is not None:
            records.append({
                'id': current_id,
                'description': current_desc,
                'sequence': "".join(current_seq)
            })
            
    return records

def write_fasta(records, file_path):
    """
    Writes sequence records to a FASTA file.
    records is a list of dictionaries containing 'id', 'sequence', and optionally 'description'.
    """
    with open(file_path, 'w') as f:
        for rec in records:
            desc = rec.get('description', '')
            header = ">{} {}".format(rec['id'], desc).strip()
            f.write(header + "\n")
            # Write sequence in blocks of 80 characters
            seq = rec['sequence']
            for i in range(0, len(seq), 80):
                f.write(seq[i:i+80] + "\n")

def smith_waterman(seq1, seq2, match_score=2, mismatch_penalty=-1, gap_penalty=-2):
    """
    Smith-Waterman algorithm for local sequence alignment.
    Returns the maximum alignment score and the alignment identity percentage.
    Highly optimized pure-python implementation.
    """
    m, n = len(seq1), len(seq2)
    if m == 0 or n == 0:
        return 0, 0.0
        
    # Initialize score matrix with zeros
    score_matrix = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    max_i, max_j = 0, 0
    
    # Fill matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Calculate match/mismatch score
            if seq1[i-1] == seq2[j-1]:
                score = match_score
            else:
                score = mismatch_penalty
                
            match = score_matrix[i-1][j-1] + score
            delete = score_matrix[i-1][j] + gap_penalty
            insert = score_matrix[i][j-1] + gap_penalty
            
            val = max(0, match, delete, insert)
            score_matrix[i][j] = val
            
            if val > max_score:
                max_score = val
                max_i, max_j = i, j
                
    if max_score == 0:
        return 0, 0.0
        
    # Traceback to calculate sequence identity within aligned region
    i, j = max_i, max_j
    aligned_matches = 0
    aligned_len = 0
    
    while i > 0 and j > 0 and score_matrix[i][j] > 0:
        val = score_matrix[i][j]
        val_diag = score_matrix[i-1][j-1]
        val_up = score_matrix[i-1][j]
        val_left = score_matrix[i][j-1]
        
        # Determine movement
        if seq1[i-1] == seq2[j-1]:
            score = match_score
        else:
            score = mismatch_penalty
            
        if val == val_diag + score:
            if seq1[i-1] == seq2[j-1]:
                aligned_matches += 1
            aligned_len += 1
            i -= 1
            j -= 1
        elif val == val_up + gap_penalty:
            aligned_len += 1
            i -= 1
        else:
            aligned_len += 1
            j -= 1
            
    identity = (aligned_matches / aligned_len) if aligned_len > 0 else 0.0
    return max_score, identity
