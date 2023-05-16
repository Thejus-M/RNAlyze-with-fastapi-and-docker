import numpy as np
import pandas as pd

def calculate_features(seq):
    # Calculate longest ORF length
    print("seq : ",seq)
    print('len',len(seq))
    longest_orf_length = 0
    for frame in range(3):
        for pos in range(frame, len(seq)-2, 3):
            codon = seq[pos:pos+3]
            if codon == 'ATG':
                orf_length = 0
                for pos2 in range(pos, len(seq)-2, 3):
                    codon2 = seq[pos2:pos2+3]
                    if codon2 in ('TAA', 'TAG', 'TGA'):
                        break
                    else:
                        orf_length += 3
                longest_orf_length = max(longest_orf_length, orf_length)
    
    # Calculate GC count
    num_bases = len(seq)
    gc_count = ((seq.count('G') + seq.count('C')) / num_bases) * 100

    # Calculate transcript length
    transcript_length = len(seq)

    # Calculate CpG island features
    cpg_islands , cpg_count = [] , 0
    
    for i in range(len(seq)-1):
        if seq[i:i+2].upper() == 'CG':
            cpg_count += 1
            if cpg_count == 1:
                cpg_islands.append(0)
        else:
            if cpg_count > 0:
                cpg_islands[-1] += 1
                cpg_count = 0
    if cpg_count > 0:
        cpg_islands[-1] += 1
    num_islands = len(cpg_islands)
    
    # Calculate base frequencies
    freq_a = seq.count('A') / num_bases
    freq_c = seq.count('C') / num_bases
    freq_g = seq.count('G') / num_bases
    freq_t = seq.count('T') / num_bases
    freq_t = 1 if freq_t==0 else freq_t
    
    # Calculate fickett score
    r_y_ratio = (freq_a + freq_g) / (freq_c + freq_t)
    a_t_ratio = freq_a / freq_t
    gc_content = freq_g + freq_c
    fickett_score = (r_y_ratio * a_t_ratio) + gc_content - 0.5
    
    dataset = [longest_orf_length, gc_count, transcript_length, num_islands, fickett_score]
    # data_np = np.array(dataset).T
    # data_pd = pd.DataFrame(data=data_np, columns=["ORF","GC Count","Transcript","CpG Island","Ficket"])
    print("values : ",dataset)
    return [dataset]

# seq = '''AAAGGGTAAGCTAGAGAGAAAAAGAAAGAACTGTCCGTCCCCCTTGGGCTTATTTAGAAACGGCTCG'''
seq = '''GCACATCCTCTCCTCTCTCCTTCTCTCTCTGCCCGGAGCTGGTTTCCGTCTCTCGGCTCG
GGGCTGGAACTCCGGCCCAACCTAGGCGCGCAGCCGCCACGAGATGGCGCACTTCCGATC
AATGTCAAAGCCGCCGGGGAGCCGGGAACCCCAGCATGATTCTTGGCCTTTGTTCGCTTC
TGATACTAAGAGCAGCACGGTACATTATTTCACTTGTCCCGCTCCCCTTCATAACAGAAA
AAGGGGACTCACCCTCAAGAAGTGATTGGTATGGTAATTTAAAGCAACGCGCATTCGCTA
GGCCTCGCGAGCGTCGCCGCGCGGAGAAGCCAGCTGTCCCTTGGCAGTGATTTCGGAAAT
GTGTCAAGTTGATAGAGAAAAACAACCCAGCGAAGGCGCCTTCTCTGAAAACAATGCTGA
GAATGAGAGCGGCGGAGACAAGCCCCCCATCGATCCCAATAACCCAGCAGCCAACTGGCT
TCATGCGCGCTCCACTCGGAAAAAGCGGTGCCCCTATACAAAACACCAGACCCTGGAACT
GGAGAAAGAGTTTCTGTTCAACATGTACCTCACCAGGGACCGCAGGTACGAGGTGGCTCG
ACTGCTCAACCTCACCGAGAGGCAGGTCAAGATCTGGTTCCAGAACCGCAGGATGAAAAT
GAAGAAAATCAACAAAGACCGAGCAAAAGACGAGTGATGCCATTTGGGCTTATTTAGAAA
AAAGGGTAAGCTAGAGAGAAAAAGAAAGAACTGTCCGTCCCCCTT'''
seq=seq.replace("\n", "")
seq=seq.replace(" ", "")
# print(seq)
# print("features ",calculate_features(seq))