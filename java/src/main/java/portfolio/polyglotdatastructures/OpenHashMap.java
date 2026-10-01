package portfolio.polyglotdatastructures;

import java.util.Objects;

/**
 * Open-addressing hash map with linear probing and tombstones.
 *
 * <p>Keys live in one flat array, which is cache-friendly compared with {@link java.util.HashMap}'s
 * per-entry nodes. The table grows once live entries plus tombstones pass 3/4 of the slots.
 *
 * @param <K> key type; must not be null
 * @param <V> value type
 */
public final class OpenHashMap<K, V> {
    private static final Object DELETED = new Object();
    private static final int INITIAL = 8;

    private Object[] keys = new Object[INITIAL];
    private Object[] values = new Object[INITIAL];
    private int size;
    private int used;

    /** Spreads the hash so that low bits depend on high bits too. */
    private static int spread(Object key) {
        int h = key.hashCode();
        return h ^ (h >>> 16);
    }

    /** Returns the slot holding key, or -1. */
    private int find(Object key) {
        int mask = keys.length - 1;
        for (int i = spread(key) & mask; ; i = (i + 1) & mask) {
            Object k = keys[i];
            if (k == null) {
                return -1;
            }
            if (k != DELETED && k.equals(key)) {
                return i;
            }
        }
    }

    /** Returns the value for key, or null. */
    @SuppressWarnings("unchecked")
    public V get(K key) {
        int i = find(Objects.requireNonNull(key));
        return i >= 0 ? (V) values[i] : null;
    }

    /** Reports whether key is present. */
    public boolean containsKey(K key) {
        return find(Objects.requireNonNull(key)) >= 0;
    }

    /** Inserts or replaces; returns the previous value or null. */
    @SuppressWarnings("unchecked")
    public V put(K key, V value) {
        int i = find(Objects.requireNonNull(key));
        if (i >= 0) {
            V old = (V) values[i];
            values[i] = value;
            return old;
        }
        if ((used + 1) * 4 > keys.length * 3) {
            resize();
        }
        int mask = keys.length - 1;
        i = spread(key) & mask;
        while (keys[i] != null && keys[i] != DELETED) {
            i = (i + 1) & mask;
        }
        if (keys[i] == null) {
            used++;
        }
        keys[i] = key;
        values[i] = value;
        size++;
        return null;
    }

    /** Deletes key; returns its value or null. */
    @SuppressWarnings("unchecked")
    public V remove(K key) {
        int i = find(Objects.requireNonNull(key));
        if (i < 0) {
            return null;
        }
        V old = (V) values[i];
        keys[i] = DELETED;
        values[i] = null;
        size--;
        return old;
    }

    /** Returns the number of live entries. */
    public int size() {
        return size;
    }

    /** Rehashes live entries into a table sized for them, dropping tombstones. */
    @SuppressWarnings("unchecked")
    private void resize() {
        Object[] oldKeys = keys;
        Object[] oldValues = values;
        int cap = INITIAL;
        while (cap * 3 < (size + 1) * 8) {
            cap *= 2;
        }
        keys = new Object[cap];
        values = new Object[cap];
        size = 0;
        used = 0;
        for (int i = 0; i < oldKeys.length; i++) {
            if (oldKeys[i] != null && oldKeys[i] != DELETED) {
                put((K) oldKeys[i], (V) oldValues[i]);
            }
        }
    }
}
