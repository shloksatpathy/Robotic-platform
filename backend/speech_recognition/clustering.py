from sklearn.cluster import AgglomerativeClustering
import numpy as np

def cluster_unknown(embeddings):
    n = len(embeddings)
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Agglomerative clustering with distance threshold
    # A cosine similarity of 0.5 translates to an L2 euclidean distance of 1.0
    clusterer = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=1.0,
        metric='euclidean',
        linkage='average'
    )

    labels = clusterer.fit_predict(embeddings)
    unique_labels = set(labels)
    
    return len(unique_labels)