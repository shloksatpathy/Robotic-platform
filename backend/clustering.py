import hdbscan
import numpy as np

def cluster_unknowns(embeddings):

    if len(embeddings) < 2:
        return 1

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=1,
        metric='euclidean'
    )

    labels = clusterer.fit_predict(embeddings)

    unique = len(set(labels))

    return unique