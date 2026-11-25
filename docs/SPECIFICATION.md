# WiDS educational matching specification v1.0
This contract is independent of the evolving C++ engine. Golden traces are regression fixtures for this contract, not an obligation to reproduce C++ quirks. Any future semantic change requires versioned documentation and matching tests.

## Foundation
One Book per symbol; integer positive ticks (except market price ignored) and whole positive quantities. Order IDs are unique while resting within a book; inputs routed by Exchange assume no simultaneous ID collisions across symbols. IDs may be reused after removal. Best price first, FIFO at equal price. Trades use resting price and aggressor timestamp.
Validation in order: invalid price (non-market), invalid quantity, duplicate resting ID, FOK feasibility (Advanced), then ACK. For each match emit TRADE then FILLED(resting) if exhausted. Emit FILLED(aggressor) if fully filled. For a partially executed remainder emit PARTIAL; a limit remainder rests, market/IOC remainder is cancelled with CANCEL_ACK. Zero execution emits no PARTIAL. Cancel removes resting order or rejects "order not found". Top and depth aggregate remaining quantities; bids descending, asks ascending; absent best is None with zero quantity; depth <= 0 empty.

## Advanced
IOC matches at limit or better, never rests. FOK checks all eligible liquidity in matching order before mutation: if insufficient REJECT "FOK not fillable" without ACK or state change. Modify validates existence, positive quantity, positive price in that order; invalid modification leaves the old order intact. Valid modify is passive (no trades), requeues at the back of the new price level even at the same price, emits only MODIFY_ACK. A crossed book can temporarily exist after passive modify; this is a deliberate teaching rule, not general exchange practice. Exchange forwards invalid-quantity/price rejects for existing IDs rather than swallowing them. Unknown ID rejects "order not found".

## Optional Cancel Newest
Only nonzero equal trader IDs trigger STP. At the first eligible self-order, emit STP_CANCEL then CANCEL_ACK for incoming; leave resting order untouched, stop, retain any earlier trades, no PARTIAL on STP cancellation. FOK precheck stops at the first eligible self-order (does not skip it); reject atomically if quantity before that point is insufficient. No Cancel Oldest, Cancel Both or historical bug compatibility requirement. Anonymous trader ID zero never triggers STP.

## Grading
Foundation: tier 1 (3 traces). Advanced: tiers 1 + 2 (7). Optional challenge: tier 3 only (Cancel Newest). Grader compares each event and top/depth after every command. Legacy fixtures not in the active manifest are archival, not normative. Run tiers separately; tier 2 is not cumulative. 
