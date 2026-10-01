import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { EmptyError, HashMap, LRUCache, MinHeap } from "../src/index.js";

const VECTORS = fileURLToPath(new URL("../../spec/vectors/", import.meta.url));
const EMPTY = { error: "empty" };

/** Uniform adapters so one runner drives every structure. */
const factories = {
  min_heap: () => {
    const h = new MinHeap();
    return {
      push: (v) => (h.push(v), null),
      pop: () => h.pop(),
      peek: () => h.peek(),
      size: () => h.size,
    };
  },
  hash_map: () => {
    const m = new HashMap();
    return {
      put: (k, v) => m.set(k, v),
      get: (k) => m.get(k),
      remove: (k) => m.delete(k),
      contains: (k) => m.has(k),
      size: () => m.size,
    };
  },
  lru_cache: (init) => {
    const c = new LRUCache(init.capacity);
    return {
      put: (k, v) => c.put(k, v),
      get: (k) => c.get(k),
      size: () => c.size,
    };
  },
};

/** Runs one operation and maps EmptyError to the vector error object. */
function apply(subject, [op, ...args]) {
  try {
    return subject[op](...args);
  } catch (e) {
    if (e instanceof EmptyError) return EMPTY;
    throw e;
  }
}

const files = readdirSync(VECTORS).filter((f) => f.endsWith(".json")).sort();
assert.ok(files.length >= 3, `no vectors found in ${VECTORS}`);

for (const file of files) {
  const doc = JSON.parse(readFileSync(VECTORS + file, "utf8"));
  for (const c of doc.cases) {
    test(`${doc.structure}: ${c.name}`, () => {
      assert.equal(c.ops.length, c.expect.length);
      const subject = factories[doc.structure](c.init);
      c.ops.forEach((op, i) => {
        assert.deepEqual(apply(subject, op), c.expect[i], `step ${i}: ${JSON.stringify(op)}`);
      });
    });
  }
}

test("LRU rejects zero capacity", () => {
  assert.throws(() => new LRUCache(0), RangeError);
});

test("HashMap rejects non-string keys", () => {
  assert.throws(() => new HashMap().set(1, 1), TypeError);
});
