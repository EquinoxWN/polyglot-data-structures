package portfolio.polyglotdatastructures;

import java.util.Arrays;
import java.util.NoSuchElementException;

/** Array-backed binary min-heap of ints: O(log n) push and pop, O(1) peek. */
public final class MinHeap {
    private int[] a = new int[8];
    private int size;

    /** Adds a value and restores heap order. */
    public void push(int value) {
        if (size == a.length) {
            a = Arrays.copyOf(a, size * 2);
        }
        a[size] = value;
        siftUp(size++);
    }

    /** Returns the smallest value without removing it. */
    public int peek() {
        if (size == 0) {
            throw new NoSuchElementException("peek from empty heap");
        }
        return a[0];
    }

    /** Removes and returns the smallest value. */
    public int pop() {
        int top = peek();
        a[0] = a[--size];
        if (size > 0) {
            siftDown(0);
        }
        return top;
    }

    /** Returns the number of values. */
    public int size() {
        return size;
    }

    /** Moves the item at i up while it is smaller than its parent. */
    private void siftUp(int i) {
        int item = a[i];
        while (i > 0) {
            int parent = (i - 1) >>> 1;
            if (a[parent] <= item) {
                break;
            }
            a[i] = a[parent];
            i = parent;
        }
        a[i] = item;
    }

    /** Moves the item at i down below any smaller child. */
    private void siftDown(int i) {
        int item = a[i];
        while (true) {
            int child = 2 * i + 1;
            if (child >= size) {
                break;
            }
            if (child + 1 < size && a[child + 1] < a[child]) {
                child++;
            }
            if (item <= a[child]) {
                break;
            }
            a[i] = a[child];
            i = child;
        }
        a[i] = item;
    }
}
