const EMPTY = undefined;
const DELETED = Symbol("deleted");
const INITIAL = 8;

/** 32-bit FNV-1a hash of a string's UTF-16 code units. */
function fnv1a(key) {
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i++) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/**
 * Open-addressing hash map with linear probing and tombstones, for string keys.
 * The table grows once live entries plus tombstones pass 3/4 of the slots.
 */
export class HashMap {
  #keys = new Array(INITIAL).fill(EMPTY);
  #values = new Array(INITIAL).fill(undefined);
  #size = 0;
  #used = 0;

  /** Number of live entries. */
  get size() {
    return this.#size;
  }

  /** Returns the slot holding key, or -1. */
  #find(key) {
    const mask = this.#keys.length - 1;
    for (let i = fnv1a(key) & mask; ; i = (i + 1) & mask) {
      const k = this.#keys[i];
      if (k === EMPTY) return -1;
      if (k !== DELETED && k === key) return i;
    }
  }

  /** Returns the value for key, or null. */
  get(key) {
    const i = this.#find(key);
    return i >= 0 ? this.#values[i] : null;
  }

  /** Reports whether key is present. */
  has(key) {
    return this.#find(key) >= 0;
  }

  /** Inserts or replaces; returns the previous value or null. */
  set(key, value) {
    if (typeof key !== "string") throw new TypeError("HashMap keys must be strings");
    let i = this.#find(key);
    if (i >= 0) {
      const old = this.#values[i];
      this.#values[i] = value;
      return old;
    }
    if ((this.#used + 1) * 4 > this.#keys.length * 3) this.#resize();
    const mask = this.#keys.length - 1;
    i = fnv1a(key) & mask;
    while (this.#keys[i] !== EMPTY && this.#keys[i] !== DELETED) i = (i + 1) & mask;
    if (this.#keys[i] === EMPTY) this.#used++;
    this.#keys[i] = key;
    this.#values[i] = value;
    this.#size++;
    return null;
  }

  /** Deletes key; returns its value or null. */
  delete(key) {
    const i = this.#find(key);
    if (i < 0) return null;
    const old = this.#values[i];
    this.#keys[i] = DELETED;
    this.#values[i] = undefined;
    this.#size--;
    return old;
  }

  /** Rehashes live entries into a table sized for them, dropping tombstones. */
  #resize() {
    const keys = this.#keys;
    const values = this.#values;
    let cap = INITIAL;
    while (cap * 3 < (this.#size + 1) * 8) cap *= 2;
    this.#keys = new Array(cap).fill(EMPTY);
    this.#values = new Array(cap).fill(undefined);
    this.#size = 0;
    this.#used = 0;
    for (let i = 0; i < keys.length; i++) {
      if (keys[i] !== EMPTY && keys[i] !== DELETED) this.set(keys[i], values[i]);
    }
  }
}
