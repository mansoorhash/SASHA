import numpy as np

def normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm < 1e-8:
        raise ValueError("Invalid embedding")

    return vector / norm