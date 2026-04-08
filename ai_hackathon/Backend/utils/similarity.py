import numpy as np


def cosine_similarity(a, b):
    """Compute cosine similarity while avoiding division by zero."""
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        # Zero vectors are treated as no match instead of raising a runtime error.
        return 0.0

    return np.dot(a, b) / denominator
