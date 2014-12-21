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
