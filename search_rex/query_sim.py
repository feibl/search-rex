def shingle(doc_string, k):
    '''Extracts a set shingles from the input string. Shingles are contiguous
    subsequences of tokens'''
    n_tokens = len(doc_string)
    shingles = set()
    for i_start in range(n_tokens-(k-1)):
        shingle = doc_string[i_start:i_start+k]
        if shingle not in shingles:
            shingles.add(shingle)
    return shingles


def jaccard_sim(X, Y):
    '''Computes the Jaccard similarity between two lists'''
    x = set(X)
    y = set(Y)
    return float(len(x & y)) / len(x | y)


class QuerySimilarity(object):
    '''Computes the similarity between two queries'''

    def compute_similarity(query_string1, query_string2):
        raise NotImplementedError()


class StringJaccardSimilarity(QuerySimilarity):
    '''Computes the jaccard similarity on string basis using shingles'''

    def __init__(self, k_shingles):
        self.k_shingles = k_shingles

    def compute_similarity(self, query_string1, query_string2):
        X = shingle(query_string1, self.k_shingles)
        Y = shingle(query_string2, self.k_shingles)
        return jaccard_sim(X, Y)