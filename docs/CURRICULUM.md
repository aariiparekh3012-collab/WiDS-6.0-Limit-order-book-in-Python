# WiDS 6.0 — final curriculum (v1.0)
Approved curriculum decisions, 25 November 2026. This is the teaching contract; release readiness is separate.

1. Two progressive correctness levels: Foundation (3 traces); Advanced (7 cumulative).
2. Independent simplified educational specification, inspired by C++, not dependent on a historical commit.
3. Guided implementation freedom: explain Python structures and review individual designs; no prescribed solution.
4. Optional Cancel Newest STP only, up to five bonus marks.
5. Selectable Basic or Intermediate benchmarking; either can earn full Week 3 marks.
6. Mentor-provided agent-based simulator with noise traders, liquidity providers and informed traders; control versus signal market.
7. Intermediate ML compulsory: EDA, features, majority and imbalance-rule baselines, logistic regression, chronological validation. Advanced ML optional.
8. Guided hybrid, 4 weeks, 6–8 hours/week: 60-min teaching, 30-min doubts, asynchronous resources, weekly individual feedback/checkpoint.
9. 4–6 mentees subject to club allocation; 30-min screening, basic Python; no finance or ML prerequisites.
10. Competitive 100-mark rubric, cohort leaderboard, individual implementations and research throughout.

## Weekly flow
| Week | Work | Checkpoint | Marks |
|---|---|---|---:|
| 1 | Price-time priority, limit/market, cancel, depth; individual design review | 3/3 traces, design notes | 25 |
| 2 | IOC, FOK, passive modify, five self-written tests | 7/7 cumulative, updated design | 20 |
| 3 | Basic repeatable measurements OR Intermediate profiling, complexity, one optimisation | Results, interpretation, 7/7 retained | 15 |
| 4 | Mentor simulator, control/signal datasets, EDA, features, logistic regression and baselines | Individual notebook and report | 30 |
| Final | 5–7 minute demo and short viva | Individual reproducible submission | 10 |

## Screening
30 minutes, 100 marks: Python fundamentals 25, logical problem-solving 25, data structures 20, learning aptitude 15, motivation/commitment 15. No prior trading knowledge required. Mentor prepares questions and answer key separately.

## Deliverables
Individual repository, source, design notes, tests, benchmark report, reproducible notebook, 3–5 page final report, demo and viva. See assignments/ and docs/RUBRIC.md.

## Release readiness
The curriculum is final. Before distribution, independently validate the educational golden traces and private Python solution, run CI and dry-run the simulator/notebook. The simulator, notebook, screening question paper, private reference and hidden tests are not supplied by this curriculum document. Do not publish private answer keys or actual mentee marks in a public repository.
