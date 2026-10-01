# ADR 0002: Generate expected results from standard-library reference models

- **Status:** Accepted

## Context

The shared vectors are the single source of truth for three implementations. If an expected
value in a vector is wrong, all three implementations would be "fixed" to match the mistake.
Long random operation sequences cannot be checked by hand.

## Decision

`spec/generate_vectors.py` replays every operation sequence against a trusted reference model
(`heapq`, `dict`, `collections.OrderedDict`) and writes the results. Random cases use a fixed
seed. The generated files are committed, and CI runs `generate_vectors.py --check` so they can
never drift from the generator.

## Consequences

- Expected results are as trustworthy as CPython's standard library.
- The vectors stay readable and reviewable in pull requests, and the Java and JS runners need no
  Python at test time.
- A structure with no standard-library equivalent (for example a B-tree with a specific node
  size) needs a simple, obviously-correct model instead, such as a sorted list.
