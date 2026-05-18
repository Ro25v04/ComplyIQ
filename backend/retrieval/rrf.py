# Reciprocal Rank Fusion merges vector and BM25 results into one ranked list

# RRF_K=60 is the value from the original Cormack et al. paper; it dampens the
# advantage of rank-1 results so neither retriever can dominate on a single strong hit
RRF_K = 60
TOP_N = 30
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
