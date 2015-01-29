"""
The case-based similarity module defines the classes that calculate the
similarity of two queries. The most important class is the NGramQuerySimilarity
which computes the Jaccard coefficient similarity over the N-grams of the
queries.
"""

from similarity_metrics import jaccard_sim
from ..refreshable import Refreshable


def shingle(doc_string, k):
    """
    Extracts a set shingles from the input string. Shingles are contiguous
    subsequences of tokens
    """
    n_chars = len(doc_string)

    if n_chars < k:
        return set([doc_string])

    shingles = set()
    for i_start in range(n_chars-(k-1)):
        shingle = doc_string[i_start:i_start+k]
        if shingle not in shingles:
            shingles.add(shingle)
    return shingles


class AbstractQuerySimilarity(Refreshable):
    """
    Computes the similarity between two queries
    """

    def get_similarity(self, from_query_string, to_query_string):
        raise NotImplementedError()


class StringJaccardSimilarity(AbstractQuerySimilarity):
    """
    Computes the jaccard similarity of the two queries' shingles
    """

    def __init__(self, k_shingles):
        """
        :param k_shingles: the size of the shingles
        """
        self.k_shingles = k_shingles

    def get_similarity(self, from_query_string, to_query_string):
        X = shingle(from_query_string, self.k_shingles)
        Y = shingle(to_query_string, self.k_shingles)
        return jaccard_sim(X, Y)

    def refresh(self, refreshed_components):
        refreshed_components.add(self)
