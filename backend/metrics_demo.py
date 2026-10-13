def hit_rate(hits):
    if not hits:
        return 0.0

    return sum(hits) / len(hits)


def reciprocal_rank(ranks):
    for rank, is_relevant in enumerate(ranks, start=1):
        if is_relevant:
            return 1.0 / rank

    return 0.0

def evaluate(results):

    hit_count = 0
    rr_sum = 0

    for relevance in results:

        # 前 3 个结果是否至少命中一次
        if any(relevance[:3]):
            hit_count += 1

        # 计算单题的倒数排名
        rr_sum += reciprocal_rank(relevance[:3])

    total = len(results)

    if total == 0:
        return 0.0, 0.0

    hit_rate = hit_count / total
    mrr = rr_sum / total

    return hit_rate, mrr



results = [
    [1, 0, 0],
    [0, 0, 1],
    [0, 0, 0]
]

hit_rate_3, mrr_3 = evaluate(results)

print(f"Hit Rate@3: {hit_rate_3:.4f}")
print(f"MRR@3: {mrr_3:.4f}")


old_results = [
    [1, 1, 0],
    [1, 0, 0],
    [1, 1, 0],
    [1, 0, 0],
    [0, 1, 1]
]

new_results = [
    [1, 1, 1],
    [0, 0, 0],
    [1, 0, 1],
    [0, 0, 0],
    [1, 0, 0]
]

for name, results in [
    ("Baseline", old_results),
    ("Smart Chunking", new_results)
]:
    hit_rate_3, mrr_3 = evaluate(results)

    hit_rate_1 = sum(
        int(any(r[:1])) for r in results
    ) / len(results)

    print(f"\n{name}")
    print(f"Hit Rate@1: {hit_rate_1:.4f}")
    print(f"Hit Rate@3: {hit_rate_3:.4f}")
    print(f"MRR@3: {mrr_3:.4f}")