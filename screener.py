import os
import pandas as pd
import numpy as np
import pickle

# Import our custom utilities
from bio_utils import translate_dna, read_fasta, smith_waterman

# Graceful degradation check for scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

def sequence_to_kmers(sequence, k=3):
    """
    Converts a sequence string into overlapping k-mers separated by spaces.
    Example: "MGGVF" with k=3 -> "MGG GGV GVF"
    """
    kmers = []
    for i in range(len(sequence) - k + 1):
        kmers.append(sequence[i:i+k])
    return " ".join(kmers)

class BioSafeScreener:
    def __init__(self, ref_fasta_path=None, match_threshold=0.75, ml_threshold=0.5):
        self.match_threshold = match_threshold
        self.ml_threshold = ml_threshold
        self.ref_threats = []
        self.exact_match_kmers = set()
        
        # Load reference threat sequences if provided
        if ref_fasta_path and os.path.exists(ref_fasta_path):
            self.load_reference_database(ref_fasta_path)
            
        # ML pipeline components
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b') # Allow single/multi-char tokens
            self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            self.vectorizer = None
            self.classifier = None
            
        self.is_trained = False
        
    def load_reference_database(self, ref_fasta_path):
        """
        Loads the database of regulated pathogens and biological threats.
        Extracts exact-match DNA k-mers (Tier 1) and sets up templates for local alignment (Tier 2).
        """
        self.ref_threats = read_fasta(ref_fasta_path)
        
        # Extract DNA 18-mers for Tier 1 exact match screening
        k = 18
        self.exact_match_kmers = set()
        for rec in self.ref_threats:
            dna_seq = rec['sequence']
            for i in range(len(dna_seq) - k + 1):
                self.exact_match_kmers.add(dna_seq[i:i+k].upper())
                
        # Also pre-translate reference sequences for homology alignment
        for rec in self.ref_threats:
            rec['protein_sequence'] = translate_dna(rec['sequence'])
            
        print("Loaded {} threat reference sequences for screening.".format(len(self.ref_threats)))
        
    def fit_ml_classifier(self, train_df):
        """
        Trains the Tier 3 ML model using amino acid k-mer TF-IDF representation.
        Expects a DataFrame with 'protein_sequence' and 'label' (1 for threat, 0 for benign).
        """
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn is not installed. Skipping Tier 3 ML training.")
            return
            
        print("Training Tier 3 ML Sequence Classifier...")
        # Convert protein sequences to space-separated k-mer strings
        kmer_docs = train_df['protein_sequence'].apply(lambda x: sequence_to_kmers(x, k=3))
        
        # Fit vectorizer and transform training data
        X = self.vectorizer.fit_transform(kmer_docs)
        y = train_df['label'].values
        
        # Train Random Forest classifier
        self.classifier.fit(X, y)
        self.is_trained = True
        print("Tier 3 ML Classifier trained successfully.")
        
    def screen_sequence(self, query_dna):
        """
        Screens a query DNA sequence through Tier 1, Tier 2, and Tier 3.
        Returns a detailed report.
        """
        query_dna = query_dna.upper().strip()
        query_protein = translate_dna(query_dna)
        
        report = {
            'query_length_nt': len(query_dna),
            'query_length_aa': len(query_protein),
            'tier1_flag': False,
            'tier2_flag': False,
            'tier3_prob': 0.0,
            'tier3_flag': False,
            'flagged': False,
            'highest_identity': 0.0,
            'best_match_ref_id': None,
            'best_match_desc': None,
            'ml_flag_reason': ""
        }
        
        # --- TIER 1: Exact DNA Match ---
        k = 18
        for i in range(len(query_dna) - k + 1):
            kmer = query_dna[i:i+k]
            if kmer in self.exact_match_kmers:
                report['tier1_flag'] = True
                report['flagged'] = True
                # Find which reference this k-mer belongs to
                for rec in self.ref_threats:
                    if kmer in rec['sequence'].upper():
                        report['best_match_ref_id'] = rec['id']
                        report['best_match_desc'] = rec['description']
                        break
                break
                
        # --- TIER 2: Homology Alignment (Protein Local Alignment) ---
        best_identity = 0.0
        best_ref_id = None
        best_ref_desc = None
        
        for rec in self.ref_threats:
            ref_protein = rec['protein_sequence']
            score, identity = smith_waterman(query_protein, ref_protein)
            if identity > best_identity:
                best_identity = identity
                best_ref_id = rec['id']
                best_ref_desc = rec['description']
                
        report['highest_identity'] = best_identity
        if best_identity >= self.match_threshold:
            report['tier2_flag'] = True
            report['flagged'] = True
            if not report['best_match_ref_id']:
                report['best_match_ref_id'] = best_ref_id
                report['best_match_desc'] = best_ref_desc
                
        # --- TIER 3: Machine Learning Classifier ---
        if SKLEARN_AVAILABLE and self.is_trained and len(query_protein) >= 3:
            query_kmer_doc = sequence_to_kmers(query_protein, k=3)
            X_query = self.vectorizer.transform([query_kmer_doc])
            prob = self.classifier.predict_proba(X_query)[0][1] # Probability of Class 1 (Threat)
            
            report['tier3_prob'] = float(prob)
            if prob >= self.ml_threshold:
                report['tier3_flag'] = True
                report['flagged'] = True
                report['ml_flag_reason'] = "Sequence classified as potential regulated family with probability {:.1f}%".format(prob * 100)
        elif not SKLEARN_AVAILABLE:
            report['ml_flag_reason'] = "Tier 3 ML Classifier disabled: scikit-learn is not installed in this environment."
            
        return report

    def save_model(self, file_path):
        """
        Saves the trained ML model components to a pickle file.
        """
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Skipping model save.")
            return
        if not self.is_trained:
            raise ValueError("Cannot save model: classifier is not trained yet.")
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'match_threshold': self.match_threshold,
            'ml_threshold': self.ml_threshold,
            'is_trained': self.is_trained
        }
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)
        print("Saved screener model to: {}".format(file_path))

    def load_model(self, file_path):
        """
        Loads the trained ML model components from a pickle file.
        """
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Skipping model load.")
            return
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.match_threshold = model_data['match_threshold']
        self.ml_threshold = model_data['ml_threshold']
        self.is_trained = model_data['is_trained']
        print("Loaded screener model from: {}".format(file_path))
