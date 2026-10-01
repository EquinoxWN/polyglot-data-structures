package portfolio.polyglotdatastructures;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.NullNode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Stream;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestFactory;

/** Replays the shared JSON vectors in ../spec/vectors against the Java implementations. */
class VectorsTest {
    private static final ObjectMapper JSON = new ObjectMapper();
    private static final JsonNodeFactory NODES = JsonNodeFactory.instance;
    private static final Path VECTORS = Path.of("..", "spec", "vectors");

    /** Uniform view over the structures so the runner stays generic. */
    private interface Subject {
        JsonNode apply(String op, JsonNode args);
    }

    private static JsonNode emptyError() {
        return NODES.objectNode().put("error", "empty");
    }

    private static JsonNode intOrNull(Integer v) {
        return v == null ? NullNode.getInstance() : NODES.numberNode(v);
    }

    private static Subject heap() {
        MinHeap h = new MinHeap();
        return (op, args) -> {
            try {
                return switch (op) {
                    case "push" -> {
                        h.push(args.get(0).asInt());
                        yield NullNode.getInstance();
                    }
                    case "pop" -> NODES.numberNode(h.pop());
                    case "peek" -> NODES.numberNode(h.peek());
                    case "size" -> NODES.numberNode(h.size());
                    default -> throw new IllegalArgumentException(op);
                };
            } catch (NoSuchElementException e) {
                return emptyError();
            }
        };
    }

    private static Subject hashMap() {
        OpenHashMap<String, Integer> m = new OpenHashMap<>();
        return (op, args) -> switch (op) {
            case "put" -> intOrNull(m.put(args.get(0).asText(), args.get(1).asInt()));
            case "get" -> intOrNull(m.get(args.get(0).asText()));
            case "remove" -> intOrNull(m.remove(args.get(0).asText()));
            case "contains" -> NODES.booleanNode(m.containsKey(args.get(0).asText()));
            case "size" -> NODES.numberNode(m.size());
            default -> throw new IllegalArgumentException(op);
        };
    }

    private static Subject lru(JsonNode init) {
        LruCache<String, Integer> c = new LruCache<>(init.get("capacity").asInt());
        return (op, args) -> switch (op) {
            case "put" -> {
                String evicted = c.put(args.get(0).asText(), args.get(1).asInt());
                yield evicted == null ? NullNode.getInstance() : NODES.textNode(evicted);
            }
            case "get" -> intOrNull(c.get(args.get(0).asText()));
            case "size" -> NODES.numberNode(c.size());
            default -> throw new IllegalArgumentException(op);
        };
    }

    private static Subject create(String structure, JsonNode init) {
        return switch (structure) {
            case "min_heap" -> heap();
            case "hash_map" -> hashMap();
            case "lru_cache" -> lru(init);
            default -> throw new IllegalArgumentException(structure);
        };
    }

    private static void run(String structure, JsonNode c) {
        Subject s = create(structure, c.get("init"));
        JsonNode ops = c.get("ops");
        JsonNode expect = c.get("expect");
        assertEquals(ops.size(), expect.size(), "ops and expect must align");
        for (int i = 0; i < ops.size(); i++) {
            JsonNode op = ops.get(i);
            List<JsonNode> args = new ArrayList<>();
            op.forEach(args::add);
            String name = args.remove(0).asText();
            JsonNode got = s.apply(name, NODES.arrayNode().addAll(args));
            assertEquals(expect.get(i), got, "step " + i + ": " + op);
        }
    }

    @TestFactory
    Stream<DynamicTest> sharedVectors() throws IOException {
        List<DynamicTest> tests = new ArrayList<>();
        try (Stream<Path> files = Files.list(VECTORS)) {
            for (Path p : files.filter(f -> f.toString().endsWith(".json")).sorted().toList()) {
                JsonNode doc = JSON.readTree(p.toFile());
                String structure = doc.get("structure").asText();
                for (JsonNode c : doc.get("cases")) {
                    tests.add(DynamicTest.dynamicTest(structure + ": " + c.get("name").asText(), () -> run(structure, c)));
                }
            }
        }
        assertFalse(tests.isEmpty(), "no vectors found in " + VECTORS.toAbsolutePath());
        return tests.stream();
    }

    @Test
    void lruRejectsZeroCapacity() {
        assertThrows(IllegalArgumentException.class, () -> new LruCache<String, Integer>(0));
    }
}
