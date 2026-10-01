# Shared test vectors

Every structure has one language-neutral spec in `vectors/<structure>.json`. The Java, Python and
JavaScript runners replay the same operations and must produce exactly the same results, so a bug in
one language is caught by the spec rather than by luck.

## Format

```json
{
  "structure": "lru_cache",
  "cases": [
    {
      "name": "evicts least recently used",
      "init": {"capacity": 2},
      "ops": [["put", "a", 1], ["put", "b", 2], ["put", "c", 3], ["get", "a"]],
      "expect": [null, null, "a", null]
    }
  ]
}
```

- `init` holds constructor arguments.
- `ops[i]` is `[operation, ...arguments]`; `expect[i]` is its result.
- `null` means "no value"; `{"error": "empty"}` means the operation must fail because the structure
  is empty.

## Operations

| Structure | Operation | Result |
|---|---|---|
| `min_heap` | `push(int)` | `null` |
| | `pop()` / `peek()` | smallest value, or `{"error": "empty"}` |
| | `size()` | count |
| `hash_map` | `put(key, int)` | previous value or `null` |
| | `get(key)` / `remove(key)` | value (removed value) or `null` |
| | `contains(key)` | boolean |
| | `size()` | count |
| `lru_cache` | `put(key, int)` | evicted key or `null` (updating a key never evicts) |
| | `get(key)` | value or `null`; a hit makes the key most recently used |
| | `size()` | count |

## Regenerating

Expected results come from standard-library reference models (`heapq`, `dict`, `OrderedDict`) in
`generate_vectors.py`, with a fixed seed for the random cases. CI runs `--check` so the committed
files can never drift from the generator.

```bash
python spec/generate_vectors.py
```
