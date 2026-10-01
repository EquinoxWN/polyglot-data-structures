/** Thrown when reading from an empty structure. */
export class EmptyError extends Error {
  constructor(message) {
    super(message);
    this.name = "EmptyError";
  }
}

/** Array-backed binary min-heap of numbers: O(log n) push and pop, O(1) peek. */
export class MinHeap {
  #a = [];

  /** Number of values. */
  get size() {
    return this.#a.length;
  }

  /** Adds a value and restores heap order. */
  push(value) {
    this.#a.push(value);
    this.#siftUp(this.#a.length - 1);
  }

  /** Returns the smallest value without removing it. */
  peek() {
    if (this.#a.length === 0) throw new EmptyError("peek from empty heap");
    return this.#a[0];
  }

  /** Removes and returns the smallest value. */
  pop() {
    const top = this.peek();
    const last = this.#a.pop();
    if (this.#a.length > 0) {
      this.#a[0] = last;
      this.#siftDown(0);
    }
    return top;
  }

  /** Moves the item at i up while it is smaller than its parent. */
  #siftUp(i) {
    const a = this.#a;
    const item = a[i];
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (a[parent] <= item) break;
      a[i] = a[parent];
      i = parent;
    }
    a[i] = item;
  }

  /** Moves the item at i down below any smaller child. */
  #siftDown(i) {
    const a = this.#a;
    const n = a.length;
    const item = a[i];
    for (;;) {
      let child = 2 * i + 1;
      if (child >= n) break;
      if (child + 1 < n && a[child + 1] < a[child]) child++;
      if (item <= a[child]) break;
      a[i] = a[child];
      i = child;
    }
    a[i] = item;
  }
}
