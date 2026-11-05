import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { EmptyError, HashMap, LRUCache, MinHeap } from "../src/index.js";
import { fnv1a } from "../src/hashMap.js";

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

test("HashMap grows past 3/4 load and keeps load at or below 3/8 after growth", () => {
  const m = new HashMap();
  for (let i = 0; i < 6; i++) m.set(`k${i}`, i);
  assert.equal(m.capacity, 8);
  m.set("k6", 6);
  assert.equal(m.capacity, 32);
});

test("HashMap reusing a tombstone does not count as a new slot", () => {
  const m = new HashMap();
  for (let i = 0; i < 5; i++) m.set(`k${i}`, i);
  m.delete("k0");
  m.set("k0", 0);
  m.set("k5", 5);
  assert.equal(m.capacity, 8);
});

test("HashMap rejects non-string keys on every operation", () => {
  const m = new HashMap();
  for (const op of [(k) => m.get(k), (k) => m.has(k), (k) => m.delete(k)]) {
    for (const key of [null, undefined, 1, {}]) assert.throws(() => op(key), TypeError);
  }
});

test("fnv1a matches the published FNV-1a 32-bit values", () => {
  assert.equal(fnv1a(""), 0x811c9dc5);
  assert.equal(fnv1a("a"), 0xe40c292c);
  assert.equal(fnv1a("foobar"), 0xbf9cf968);
});

test("LRU rejects a capacity that is not a positive integer", () => {
  for (const c of [1.5, NaN, "2", -1]) assert.throws(() => new LRUCache(c), RangeError);
});

test("MinHeap rejects NaN and non-numbers", () => {
  const h = new MinHeap();
  for (const v of [NaN, "1", null, undefined]) assert.throws(() => h.push(v), TypeError);
  assert.equal(h.size, 0);
});
