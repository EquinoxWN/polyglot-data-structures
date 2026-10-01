/** Fixed-capacity least-recently-used cache with O(1) get and put. */
export class LRUCache {
  #capacity;
  #index = new Map();
  /** Sentinel: head.next is most recent, head.prev least recent. */
  #head;

  /** Creates a cache holding at most capacity entries. */
  constructor(capacity) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new RangeError("capacity must be an integer of at least 1");
    }
    this.#capacity = capacity;
    this.#head = { key: undefined, value: undefined };
    this.#head.prev = this.#head;
    this.#head.next = this.#head;
  }

  /** Number of cached entries. */
  get size() {
    return this.#index.size;
  }

  /** Returns the value and marks key most recent, or null. */
  get(key) {
    const node = this.#index.get(key);
    if (node === undefined) return null;
    this.#unlink(node);
    this.#pushFront(node);
    return node.value;
  }

  /** Inserts or updates key; returns the evicted key or null. */
  put(key, value) {
    let node = this.#index.get(key);
    if (node !== undefined) {
      node.value = value;
      this.#unlink(node);
      this.#pushFront(node);
      return null;
    }
    let evicted = null;
    if (this.#index.size === this.#capacity) {
      const lru = this.#head.prev;
      this.#unlink(lru);
      this.#index.delete(lru.key);
      evicted = lru.key;
    }
    node = { key, value };
    this.#index.set(key, node);
    this.#pushFront(node);
    return evicted;
  }

  /** Removes node from the recency list. */
  #unlink(node) {
    node.prev.next = node.next;
    node.next.prev = node.prev;
  }

  /** Inserts node as most recently used. */
  #pushFront(node) {
    node.prev = this.#head;
    node.next = this.#head.next;
    this.#head.next.prev = node;
    this.#head.next = node;
  }
}
