# Week 4: Quantitative research

**Question:** can depth imbalance and order-flow imbalance (OFI) predict short-term mid-price changes in a simulated market? Keep contemporaneous price impact separate from out-of-sample predictability.

Your mentor releases the order-flow simulator and the notebook template in Week 4. You run it through your own engine.

**Hand in**
- A reproducible generator setting: seed and configuration.
- Data quality summary, class counts and feature plots.
- Features: spread, mid-price, depth imbalance, OFI, signed trade volume, rolling volatility and lagged returns.
- Target: `sign(mid[t+10] - mid[t])`, ten command observations ahead. Classes: down (-1), unchanged (0), up (+1).
- A chronological split inside each sequence (60% train, 20% validation, 20% test), labels purged near the boundaries, preprocessing fitted on train only.
- Models: majority-class baseline, an imbalance-threshold rule, and logistic regression.
- Metrics: accuracy, balanced accuracy, macro F1, confusion matrix, comparison with baselines, stability across seeds.
- A comparison of the control market and the signal market.
- A 4 to 6 page report (abstract, introduction, engine architecture, correctness, performance, research method, results, limitations, conclusion) and a short live demo.

**Rules:** never put future data into a feature. Never use the simulator's hidden fair value as a feature.
A null result is fine. Predicting well on synthetic data does not show a real trading edge.
