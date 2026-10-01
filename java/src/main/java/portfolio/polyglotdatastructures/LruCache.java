package portfolio.polyglotdatastructures;

import java.util.HashMap;
import java.util.Map;

/**
 * Fixed-capacity least-recently-used cache with O(1) get and put.
 *
 * @param <K> key type
 * @param <V> value type
 */
public final class LruCache<K, V> {
    private static final class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev = this;
        Node<K, V> next = this;
    }

    private final int capacity;
    private final Map<K, Node<K, V>> index = new HashMap<>();
    /** Sentinel: head.next is most recent, head.prev least recent. */
    private final Node<K, V> head = new Node<>();

    /** Creates a cache holding at most capacity entries. */
    public LruCache(int capacity) {
        if (capacity < 1) {
            throw new IllegalArgumentException("capacity must be at least 1");
        }
        this.capacity = capacity;
    }

    /** Returns the value and marks key most recent, or null. */
    public V get(K key) {
        Node<K, V> node = index.get(key);
        if (node == null) {
            return null;
        }
        unlink(node);
        pushFront(node);
        return node.value;
    }

    /** Inserts or updates key; returns the evicted key or null. */
    public K put(K key, V value) {
        Node<K, V> node = index.get(key);
        if (node != null) {
            node.value = value;
            unlink(node);
            pushFront(node);
            return null;
        }
        K evicted = null;
        if (index.size() == capacity) {
            Node<K, V> lru = head.prev;
            unlink(lru);
            index.remove(lru.key);
            evicted = lru.key;
        }
        node = new Node<>();
        node.key = key;
        node.value = value;
        index.put(key, node);
        pushFront(node);
        return evicted;
    }

    /** Returns the number of cached entries. */
    public int size() {
        return index.size();
    }

    /** Removes node from the recency list. */
    private void unlink(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    /** Inserts node as most recently used. */
    private void pushFront(Node<K, V> node) {
        node.prev = head;
        node.next = head.next;
        head.next.prev = node;
        head.next = node;
    }
}
