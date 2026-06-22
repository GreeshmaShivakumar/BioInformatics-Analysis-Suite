"""
Advanced bioinformatics analysis functions
Includes: ORF detection, translation, repeats, dinucleotides, alignment, etc.
"""

from Bio import SeqIO, Seq, SeqUtils, pairwise2
from Bio.Seq import translate
from typing import Dict, List, Tuple, Any
import json
import re
from collections import defaultdict, Counter

def get_quality_scores(fastq_path: str) -> Dict[str, Any]:
    """Extract quality score information from FASTQ file"""
    quality_data = {
        "per_position_quality": defaultdict(list),
        "per_sequence_quality": [],
        "quality_stats": {}
    }
    
    for record in SeqIO.parse(fastq_path, "fastq"):
        quality_scores = record.letter_annotations.get("phred_quality", [])
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            quality_data["per_sequence_quality"].append({
                "id": record.id,
                "average_quality": round(avg_quality, 2),
                "min_quality": min(quality_scores),
                "max_quality": max(quality_scores)
            })
            
            for pos, qual in enumerate(quality_scores):
                quality_data["per_position_quality"][pos].append(qual)
    
    # Calculate per-position statistics
    position_stats = {}
    for pos, quals in quality_data["per_position_quality"].items():
        if quals:
            position_stats[pos] = {
                "avg": round(sum(quals) / len(quals), 2),
                "min": min(quals),
                "max": max(quals),
                "median": sorted(quals)[len(quals)//2]
            }
    
    quality_data["per_position_quality"] = position_stats
    return quality_data


def get_base_frequency_heatmap(fasta_path: str, window_size: int = 100) -> Dict[str, Any]:
    """Generate base frequency heatmap data across sequences"""
    heatmap_data = {
        "sequences": [],
        "frequency_matrix": []
    }
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq).upper()
        seq_frequencies = []
        
        for i in range(0, len(seq_str), window_size):
            window = seq_str[i:i+window_size]
            total = len(window)
            frequencies = {
                "A": round((window.count('A') / total) * 100, 2) if total > 0 else 0,
                "T": round((window.count('T') / total) * 100, 2) if total > 0 else 0,
                "G": round((window.count('G') / total) * 100, 2) if total > 0 else 0,
                "C": round((window.count('C') / total) * 100, 2) if total > 0 else 0,
            }
            seq_frequencies.append(frequencies)
        
        heatmap_data["sequences"].append({
            "id": record.id,
            "length": len(record.seq),
            "frequencies": seq_frequencies
        })
    
    return heatmap_data


def find_orfs(fasta_path: str, min_length: int = 100) -> Dict[str, Any]:
    """Find Open Reading Frames in sequences"""
    orfs_data = {
        "sequences": [],
        "total_orfs": 0
    }
    
    start_codon = "ATG"
    stop_codons = ["TAA", "TAG", "TGA"]
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq).upper()
        seq_orfs = []
        
        # Search all 6 reading frames
        for frame in range(3):
            for strand in [seq_str, str(Seq.reverse_complement(Seq.Seq(seq_str)))]:
                for i in range(frame, len(strand) - 3, 3):
                    codon = strand[i:i+3]
                    if codon == start_codon:
                        # Look for stop codon
                        for j in range(i + 3, len(strand) - 3, 3):
                            stop_codon = strand[j:j+3]
                            if stop_codon in stop_codons:
                                orf_length = j + 3 - i
                                if orf_length >= min_length:
                                    seq_orfs.append({
                                        "start": i,
                                        "end": j + 3,
                                        "length": orf_length,
                                        "frame": frame,
                                        "strand": "+" if strand == seq_str else "-",
                                        "sequence": strand[i:j+3]
                                    })
                                break
        
        orfs_data["sequences"].append({
            "id": record.id,
            "length": len(seq_str),
            "orfs": seq_orfs
        })
        orfs_data["total_orfs"] += len(seq_orfs)
    
    return orfs_data


def translate_dna_to_protein(fasta_path: str) -> Dict[str, Any]:
    """Translate DNA sequences to protein"""
    protein_data = {
        "sequences": []
    }
    
    codon_table = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
        'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
        'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
    }
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq).upper()
        protein = ""
        
        for i in range(0, len(seq_str) - 2, 3):
            codon = seq_str[i:i+3]
            protein += codon_table.get(codon, 'X')
        
        protein_data["sequences"].append({
            "id": record.id,
            "dna_length": len(seq_str),
            "protein_length": len(protein),
            "protein": protein,
            "dna": seq_str
        })
    
    return protein_data


def get_dinucleotide_frequency(fasta_path: str) -> Dict[str, Any]:
    """Calculate dinucleotide and trinucleotide frequencies"""
    freq_data = {
        "sequences": [],
        "global_dinucleotides": {},
        "global_trinucleotides": {}
    }
    
    global_dinuc = Counter()
    global_trinuc = Counter()
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq).upper()
        
        # Dinucleotides
        dinuc_freq = Counter()
        for i in range(len(seq_str) - 1):
            dinuc = seq_str[i:i+2]
            if 'N' not in dinuc:
                dinuc_freq[dinuc] += 1
                global_dinuc[dinuc] += 1
        
        # Trinucleotides
        trinuc_freq = Counter()
        for i in range(len(seq_str) - 2):
            trinuc = seq_str[i:i+3]
            if 'N' not in trinuc:
                trinuc_freq[trinuc] += 1
                global_trinuc[trinuc] += 1
        
        freq_data["sequences"].append({
            "id": record.id,
            "length": len(seq_str),
            "dinucleotides": dict(dinuc_freq.most_common(16)),
            "trinucleotides": dict(trinuc_freq.most_common(16))
        })
    
    freq_data["global_dinucleotides"] = dict(global_dinuc.most_common(16))
    freq_data["global_trinucleotides"] = dict(global_trinuc.most_common(16))
    
    return freq_data


def find_repeats(fasta_path: str, min_repeat_length: int = 10) -> Dict[str, Any]:
    """Find repetitive sequences"""
    repeat_data = {
        "sequences": [],
        "total_repeats": 0
    }
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq).upper()
        repeats = []
        
        # Find tandem repeats
        for unit_length in range(2, min(50, len(seq_str) // 2)):
            for start in range(len(seq_str) - unit_length * 2):
                unit = seq_str[start:start + unit_length]
                
                # Check for repeats of this unit
                repeat_count = 1
                pos = start + unit_length
                while pos + unit_length <= len(seq_str):
                    if seq_str[pos:pos + unit_length] == unit:
                        repeat_count += 1
                        pos += unit_length
                    else:
                        break
                
                if repeat_count >= 2 and repeat_count * unit_length >= min_repeat_length:
                    repeats.append({
                        "type": "tandem",
                        "unit": unit,
                        "unit_length": unit_length,
                        "repeat_count": repeat_count,
                        "total_length": repeat_count * unit_length,
                        "start": start
                    })
        
        repeat_data["sequences"].append({
            "id": record.id,
            "length": len(seq_str),
            "repeats": repeats[:20]  # Limit to top 20
        })
        repeat_data["total_repeats"] += len(repeats)
    
    return repeat_data


def simple_sequence_alignment(seq1: str, seq2: str) -> Dict[str, Any]:
    """Simple pairwise sequence alignment"""
    match_bonus = 1
    mismatch_penalty = -1
    gap_penalty = -2
    
    alignments = pairwise2.align.globalms(seq1, seq2, match_bonus, mismatch_penalty, gap_penalty, gap_penalty)
    
    if alignments:
        best = alignments[0]
        aligned_seq1, aligned_seq2, score, _, _ = best
        
        matches = sum(1 for a, b in zip(aligned_seq1, aligned_seq2) if a == b)
        alignment_length = len(aligned_seq1)
        identity = (matches / alignment_length * 100) if alignment_length > 0 else 0
        
        return {
            "seq1_aligned": aligned_seq1,
            "seq2_aligned": aligned_seq2,
            "score": score,
            "identity": round(identity, 2),
            "matches": matches,
            "alignment_length": alignment_length
        }
    
    return {"error": "No alignment found"}


def multiple_sequence_alignment(fasta_path: str, max_sequences: int = 10) -> Dict[str, Any]:
    """Multiple sequence alignment (simple version)"""
    sequences = []
    
    for i, record in enumerate(SeqIO.parse(fasta_path, "fasta")):
        if i >= max_sequences:
            break
        sequences.append({
            "id": record.id,
            "sequence": str(record.seq).upper()
        })
    
    if len(sequences) < 2:
        return {"error": "At least 2 sequences required"}
    
    # Simple alignment using first sequence as reference
    ref_seq = sequences[0]["sequence"]
    alignments = []
    
    for seq_data in sequences[1:]:
        alignment = simple_sequence_alignment(ref_seq, seq_data["sequence"])
        alignments.append({
            "reference": sequences[0]["id"],
            "query": seq_data["id"],
            **alignment
        })
    
    return {
        "sequences": sequences,
        "alignments": alignments,
        "reference_id": sequences[0]["id"]
    }


def blast_local_search(query_seq: str, subject_sequences: Dict[str, str], threshold: float = 0.7) -> Dict[str, Any]:
    """Local BLAST-like search against subject sequences"""
    word_size = 11
    results = {
        "query": query_seq[:100],
        "hits": []
    }
    
    for seq_id, subject in subject_sequences.items():
        for i in range(len(subject) - word_size):
            word = subject[i:i + word_size]
            if word in query_seq:
                # Found a match, extend it
                matches = 0
                j = 0
                while i + j < len(subject) and j < len(query_seq):
                    if subject[i + j] == query_seq[j]:
                        matches += 1
                    j += 1
                
                identity = matches / j if j > 0 else 0
                if identity >= threshold:
                    results["hits"].append({
                        "subject_id": seq_id,
                        "start": i,
                        "length": j,
                        "identity": round(identity * 100, 2),
                        "subject_sequence": subject[i:i+j]
                    })
    
    return results
