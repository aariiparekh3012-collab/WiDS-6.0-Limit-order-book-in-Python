# Week 3: Performance (15 marks)
Choose Basic or Intermediate; both can earn full marks.

## Basic
Run python bench.py --n 10000, --n 100000 and --n 200000, five repetitions each with same machine/Python/seed 42. Record in templates/benchmark.csv. Report median and range, workload, reproducibility, differences and limitations. Explain results in 1–2 pages.

## Intermediate
Complete Basic, also use python -m cProfile -s cumtime bench.py --n 50000, analyse submit/cancel/top/depth complexity, try one optimisation, repeat benchmark and report before/after (speedup = optimised/baseline). A negative result is acceptable. Memory profiling or equivalent-workload C++ comparison optional.

Both: retain 7/7 mandatory traces. No absolute throughput target. Optional Cancel Newest only: python grade.py --tier 3, up to five bonus marks per rubric.
