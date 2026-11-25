# Week 2: Advanced order types

**Level 2 (Advanced), 20 marks.** Individual submission.

**Goal:** add IOC, FOK and passive modify without breaking Week 1.

**Hand in**
- `python grade.py --tier 1` and `python grade.py --tier 2` both green: 7/7 mandatory traces.
- `tests/test_edge_cases.py` with **five tests you wrote yourself**. Pick from this list or find your own:

| Edge case | Expected result |
|---|---|
| IOC, not enough liquidity | TRADE(s), PARTIAL when applicable, CANCEL_ACK |
| IOC, no eligible liquidity | ACK, CANCEL_ACK |
| FOK, not enough liquidity | REJECT, no trade and no change to the book |
| FOK across several levels | full execution at resting prices |
| Modify, unknown id | REJECT |
| Modify, invalid quantity or price | reject in validation order, preserve old order; router forwards the actual reason |
| Modify, same price | moves to the back of the queue |
| Modify, crossing price | passive: no matching |

- An updated `templates/design.md`: how did IOC, FOK and modify change your design?

**Acceptance:** 7/7 mandatory traces, five edge tests that pass, updated design explanation.
Modify being passive and losing queue priority are choices of this project's contract, not rules of every exchange.
