# Python design guide
Choose your own implementation, guided by the common [specification](SPECIFICATION.md). No required internal architecture.

| Structure | Possible role | Trade-off |
|---|---|---|
| dict | Order ID index or price-level map | Average O(1) lookup; finding best price by scan costs O(m) |
| deque | FIFO queue | O(1) append/popleft; arbitrary removal O(n) |
| OrderedDict or insertion-ordered dict | FIFO queue keyed by order ID | Average O(1) keyed removal; manage empty levels |
| sorted list + bisect | Price-level ordering | O(log m) search, O(m) insertion/deletion |
| heap + dict | Best-price lookup | O(log m) push/pop, stale entries need cleanup; sorted depth is separate |

Define n (orders), m (price levels), k (levels requested), and number of fills for your complexity discussion. Matching cost depends on levels and orders visited, not just one lookup. Design an index and queue strategy, sketch invariants and discuss trade-offs before implementation. Test before optimising. No C++ performance claims apply automatically to Python.

Read the specification for FIFO, validation, FOK, passive modification and optional Cancel Newest. Use integer ticks. Do not change supplied types, events, router, grader or golden fixtures. 
