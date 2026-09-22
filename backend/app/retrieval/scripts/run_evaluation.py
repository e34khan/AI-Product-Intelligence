import json

from app.db.session import SessionLocal
from app.retrieval.bm25 import build_index
from app.retrieval.dense import retrieve
from app.retrieval.hybrid import hybrid_retrieve
from app.retrieval.rerank import rerank

K = 5
BENCHMARK_PATH = "../eval/datasets/retrieval_benchmark.json"
RESULTS_PATH = "../eval/results/retrieval_evaluation.json"


def load_benchmark() -> list[dict]:
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        return json.load(f)


# each of these normalizes one method's differently-shaped results down to a
# plain, ordered list of chunk ids, so the scoring code below doesn't need to
# know or care which method produced them

def dense_ids(session, question, product_id, k) -> list[int]:
    results = retrieve(session, question, product_id=product_id, k=k)
    return [chunk.id for chunk, _distance in results]


def bm25_ids(bm25_index, question, product_id, k) -> list[int]:
    results = bm25_index.search(question, k=k, product_id=product_id)
    return [chunk_id for chunk_id, _score in results]


def hybrid_ids(session, bm25_index, question, product_id, k) -> list[int]:
    results = hybrid_retrieve(session, bm25_index, question, product_id=product_id, k=k)
    return [chunk.id for chunk, _score in results]


def rerank_ids(session, bm25_index, question, product_id, k, candidates=20) -> list[int]:
    # widen first with hybrid, then rerank narrows back down to k, same
    # two-stage shape we used in demo_rerank.py
    wide_results = hybrid_retrieve(session, bm25_index, question, product_id=product_id, k=candidates)
    chunks = [chunk for chunk, _score in wide_results]
    reranked = rerank(question, chunks, k=k)
    return [chunk.id for chunk, _score in reranked]


def recall_at_k(retrieved_ids: list[int], relevant_ids: list[int]) -> float:
    hits = len(set(retrieved_ids) & set(relevant_ids))
    return hits / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[int], relevant_ids: list[int]) -> float:
    relevant_set = set(relevant_ids)
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_set:
            return 1 / rank
    return 0.0  # none of the retrieved chunks were relevant at all


def main() -> None:
    benchmark = load_benchmark()
    session = SessionLocal()
    bm25_index = build_index(session)

    methods = {
        "dense": lambda q, pid: dense_ids(session, q, pid, K),
        "bm25": lambda q, pid: bm25_ids(bm25_index, q, pid, K),
        "hybrid": lambda q, pid: hybrid_ids(session, bm25_index, q, pid, K),
        "hybrid+rerank": lambda q, pid: rerank_ids(session, bm25_index, q, pid, K),
    }

    scores = {name: {"recall": [], "rr": []} for name in methods}

    for example in benchmark:
        question = example["question"]
        product_id = example["product_id"]
        relevant_ids = example["relevant_chunk_ids"]

        for name, run_method in methods.items():
            retrieved_ids = run_method(question, product_id)
            scores[name]["recall"].append(recall_at_k(retrieved_ids, relevant_ids))
            scores[name]["rr"].append(reciprocal_rank(retrieved_ids, relevant_ids))

    session.close()

    summary = {}
    print(f"{'method':<15} {'Recall@' + str(K):<12} {'MRR':<10}")
    for name, method_scores in scores.items():
        avg_recall = sum(method_scores["recall"]) / len(method_scores["recall"])
        avg_rr = sum(method_scores["rr"]) / len(method_scores["rr"])
        summary[name] = {"recall_at_k": avg_recall, "mrr": avg_rr}
        print(f"{name:<15} {avg_recall:<12.4f} {avg_rr:<10.4f}")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"k": K, "num_questions": len(benchmark), "methods": summary}, f, indent=2)


if __name__ == "__main__":
    main()
