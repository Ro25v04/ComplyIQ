# Reciprocal Rank Fusion merges vector and BM25 results into one ranked list

RRF_K = 60
TOP_N = 30

#rrf function that takes in a list of vector search and bm25 result lists and returns a merged rrf list with scores
def reciprocal_rank_fusion(vector_results: list[dict], bm25_results: list[dict]) -> list[dict]:
    rrf_scores = {}  # chunk_id -> combined RRF score
    chunk_data = {}  # chunk_id -> chunk dict (to retrieve later)

    # score vector search results by rank position
    for rank, chunk in enumerate(vector_results, start=1):
        chunk_id = chunk["chunk_id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rank + RRF_K)
        chunk_data[chunk_id] = chunk

    # add BM25 rank scores on top
    for rank, chunk in enumerate(bm25_results, start=1):
        chunk_id = chunk["chunk_id"]
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (rank + RRF_K)
        chunk_data[chunk_id] = chunk

    # sort all chunks by combined RRF score, highest first
    sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)

    # return top 30 with their RRF scores attached
    results = []
    for chunk_id in sorted_ids[:TOP_N]:
        chunk = chunk_data[chunk_id]
        chunk["rrf_score"] = rrf_scores[chunk_id]
        results.append(chunk)

    return results
