
def renumber(results):
    pos = {}
    for idx, val in enumerate(results):
        pos.setdefault(val, []).append(idx)
    cleared = [x for x in results if x]
    for idx, val in enumerate(sorted(cleared, key=lambda x: int(x))):
        for i in pos[val]:
            results[i] = f"{idx + 1}"
    return results
