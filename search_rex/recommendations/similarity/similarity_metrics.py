import math


def jaccard_sim(list_a, list_b):
    """
    Computes the Jaccard coefficient between two lists

    If the two lists are empty NaN is returned
    """
    set_a = set(list_a)
    set_b = set(list_b)

    if len(set_a) == 0 and len(set_b) == 0:
        return float('NaN')

    len_intersection = len(set_a & set_b)
    len_union = len(set_a | set_b)

    return float(len_intersection) / len_union


def norm(vector):
    """
    Computes the norm of a vector
    """
    return math.sqrt(sum([value**2 for value in vector.values()]))


def cosine_sim(vector1, vector2):
    """
    Computes the cosine similarity between two vectors

    If the two vectors are empty NaN is returned
    """
    if len(vector1) == 0 and len(vector2) == 0:
        return float('NaN')

    if len(vector1) == 0 or len(vector2) == 0:
        return 0.0

    dot_product = 0.0
    for attribute in vector1.keys():
        if attribute in vector2:
            dot_product += vector1[attribute] * vector2[attribute]

    if dot_product == 0.0:
        return 0.0

    return dot_product / (norm(vector1) * norm(vector2))
