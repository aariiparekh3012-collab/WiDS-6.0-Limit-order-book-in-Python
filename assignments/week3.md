# Week 3: Performance

**Goal:** measure your engine honestly, find the slowest operation, make one change, and show what happened.

**Hand in**
- Benchmark results in `templates/benchmark.csv`. Same machine, same Python, same workload and seed every time. Run each configuration **five times** and report the median and range.
  ```bash
  python bench.py --n 10000
  python bench.py --n 100000
  python bench.py --n 200000
  python -m cProfile -s cumtime bench.py --n 50000
  ```
- A written report (`templates/report.md` style, 1 to 2 pages): machine and Python version, what the profile showed, the one optimisation you tried, and before and after numbers.
  Speedup = optimised throughput / baseline throughput. Improvement % = (speedup - 1) x 100.
- A complexity analysis of `submit`, `cancel`, `top` and `depth` for your final design.
- `python grade.py --tier 1` and `--tier 2` still 7/7 after your optimisation.

**Acceptance:** 7/7 mandatory traces, a reproducible benchmark report, one tested optimisation attempt. A negative result (it did not help) is fine if you explain why.
Do not compare your Python numbers with any C++ numbers unless the workload is the same.

**Optional:** Tier 3 self-trade prevention (`python grade.py --tier 3`), worth up to 5 bonus marks.
