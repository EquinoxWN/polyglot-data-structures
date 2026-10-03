# RFC 0001: polyglot-data-structures design

- **Status:** Accepted (M1 implemented)
- **Author:** EquinoxWN
- **Created:** 2026

## Problem

"Use a hash map" is easy advice; knowing which map, why it is fast, and whether two
implementations really behave the same is not. Hand-written structures in several languages drift
apart in edge cases (empty pops, updates that should not evict, tombstones) and ordinary unit tests,
written separately per language, rarely notice. This project keeps one language-neutral spec per
structure and makes the Java, Python and JavaScript versions prove they agree with it.

## Goals

- One JSON spec per structure: operation sequences plus expected results.
- A small runner in each language replays every vector; all three must pass the same files.
- Expected results come from trusted standard-library reference models, not from hand calculation.
- Later: property-based tests for invariants (M2), benchmarks in each language's standard harness
  (M2) and a measured write-up of cache effects against the standard library (M3).

## Non-goals

- Replacing the standard library. The comparison with `java.util`, `dict` and `Map` is the point.
- Thread safety; every structure is single-threaded.
- Running as a hosted production service.

## Proposed design

![architecture](../architecture.png)

```
spec/generate_vectors.py ──► spec/vectors/*.json ──► java  VectorsTest (JUnit dynamic tests)
   (heapq, dict,                                 ├─► python test_vectors.py (pytest)
    OrderedDict models)                          └─► js     vectors.test.js (node:test)
```

### Vector format

Each case has `init` (constructor arguments), `ops` (`[name, ...args]`) and `expect` (one result
per op). `null` means "no value" and `{"error": "empty"}` means the op must fail on an empty
structure. See `spec/README.md`.

### Structures in M1

| Structure | Design | Why it is in M1 |
|---|---|---|
| Binary min-heap | Flat array, sift up/down with a hole instead of swaps | Priority queues; heap-order invariant for M2 property tests |
| Hash map | Open addressing, linear probing, tombstones, grow at 3/4 load | The "how does your hash map work?" question; cache-friendly layout |
| LRU cache | Hash index plus doubly linked list with a sentinel | The classic interview round; O(1) get and put |

The architecture map lists the rest (dynamic array, deque, chaining and Robin Hood hashing,
red-black tree, B-tree, trie, union-find, skip list). Each one joins by adding a generator model,
a vector file and three implementations; the runners do not change.

## Alternatives considered

| Option | Why not (yet) |
|---|---|
| Separate hand-written unit tests per language | Exactly how the implementations drift; no single source of truth. |
| Hand-written expected results in the JSON | Error-prone for long random sequences. Generating from `heapq` / `dict` / `OrderedDict` makes the oracle trustworthy (ADR 0002). |
| One implementation compiled to three targets | Hides the per-language differences (GC, object layout) that the benchmarks in M2 and M3 exist to show. |
| Separate chaining for the hash map | Simpler deletes, but one allocation per entry and pointer chasing; open addressing is the faster, more interesting default. Chaining returns in M2 as a benchmark comparison. |
| Protocol Buffers or YAML for vectors | JSON is readable and parses with the standard library in Python and JS and with Jackson in Java. |

## Measurement plan

- M1: 21 shared vector cases (about 5,000 operations), all passing in Java, Python and JavaScript.
- M2: operations per second at 10^3 to 10^6 elements with JMH, pyperf and mitata.
- M3: comparison against `java.util.HashMap`, Python `dict` and JS `Map`, plus hardware-counter
  evidence (cache misses) for the cache-effects write-up.

## Milestones

- **M1 (done):** vector format, generator with `--check`, three runners, heap, hash map, LRU cache.
- **M2:** property-based tests (jqwik, Hypothesis, fast-check); benchmarks; more structures.
- **M3:** cache-effects write-up and standard-library comparison with real numbers.

## Risks and open questions

- Integer semantics differ (Java `int` overflow, JS doubles, Python big ints). Vectors keep values
  inside ±10^6 so all three agree; M2 property tests must respect the same bound.
- Python's string hash is randomised per process. Behaviour is still deterministic because tests
  check results, not iteration order.
