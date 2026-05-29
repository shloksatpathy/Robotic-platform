from speechbrain.inference import EncoderClassifier
import torch
import numpy as np

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb"
)

def extract_embedding(audio):

    signal = torch.tensor(audio).unsqueeze(0)

    embedding = classifier.encode_batch(signal)

    embedding = embedding.squeeze().cpu().detach().numpy()

    norm = np.linalg.norm(embedding)

    if norm > 0:
        embedding = embedding / norm

    return embedding.astype(np.float32)