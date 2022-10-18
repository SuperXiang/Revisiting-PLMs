from esm import Alphabet, FastaBatchedDataset, ProteinBertModel, pretrained, MSATransformer
import pandas as pd
from tqdm import tqdm
from Bio import SeqIO
import itertools
from typing import List, Tuple
import torch
import scipy.stats
import numpy as np
#from BLAT_ECOLX_Ostermeier2014 import seq,res
from BLAT_ECOLX_Ranganathan2015 import seq,res

def spearmanr(target, prediction):
    target_array = np.asarray(target)
    prediction_array = np.asarray(prediction)
    return scipy.stats.mstats.spearmanr(target_array, prediction_array).correlation

def read_msa(filename: str, nseq: int) -> List[Tuple[str, str]]:
    """ Reads the first nseq sequences from an MSA file, automatically removes insertions."""

    msa = [
        (record.description, str(record.seq))
        for record in itertools.islice(SeqIO.parse(filename, "fasta"), nseq)
    ]
    msa = [(desc, seq.upper()) for desc, seq in msa]
    return msa

res_spearman=[]
for i in range(5,6):
    model, alphabet = pretrained.load_model_and_alphabet('/home/my/nips/pretrained_models/esm1v_t33_650M_UR90S_'+str(i)+'.pt')
    model.eval()
    data = [read_msa('/home/my/nips/mutation/mutation_data/msa/BLAT_ECOLX_1_b0.5.a3m', 1)][0]
    batch_converter = alphabet.get_batch_converter()
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    result=model(batch_tokens)['logits'][0][1:]
    result=torch.log_softmax(result,dim=1)
    seq_res=[]
    exp_res=[]
    for i in range(len(seq)):
        count=int(seq[i][1:-1])-24
        mutation=alphabet.get_idx(seq[i][-1])
        origin=alphabet.get_idx(seq[i][0])
        seq_res.append(result[count][mutation].detach().numpy()-result[count][origin].detach().numpy())
    for i in range(len(res)):
        exp_res.append(float(res[i]))
    print(spearmanr(seq_res,exp_res))