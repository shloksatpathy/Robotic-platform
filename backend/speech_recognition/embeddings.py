import torch 
from speechbrain.pretrained import EncoderClassifier
import numpy as np

classifier = EncoderClassifier.from_hyparams(
    source="speechbrain/spkrec-ecapa-voxceleb"
)

def extract_embeddings(audio):

    signal= torch.tensor(audio).unsqueeze(0)

    embeddings = classifier.encode_batch(signal)

    return embeddings.squeeze().detach().cpu().numpy()

    