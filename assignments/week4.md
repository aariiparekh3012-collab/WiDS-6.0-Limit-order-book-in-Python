# Week 4: Quantitative research

**Question:** can depth imbalance and order-flow imbalance (OFI) predict short-term mid-price changes in a simulated market? Keep contemporaneous price impact separate from out-of-sample predictability.

Individual assignment (30 marks). Your mentor supplies an agent-based simulator (noise traders, liquidity providers, informed traders) and notebook template in Week 4. Run control and signal configurations through your own engine. NumPy, pandas, Matplotlib and scikit-learn permitted; logistic regression compulsory, Random Forest optional. Handle empty or crossed snapshots explicitly, preserve original command indices when constructing the target.

**Hand in**
- A reproducible generator setting: seed and configuration.
- Data quality summary, class counts and feature plots.
- Features: spread, mid-price, depth imbalance, OFI, signed trade volume, rolling volatility and lagged returns.
- Target: `sign(mid[t+10] - mid[t])`, ten command observations ahead. Classes: down (-1), unchanged (0), up (+1).
- A chronological split inside each sequence (60% train, 20% validation, 20% test), labels purged near the boundaries, preprocessing fitted on train only.
- Models: majority-class baseline, an imbalance-threshold rule, and logistic regression.
- Metrics: accuracy, balanced accuracy, macro F1, confusion matrix, comparison with baselines, stability across seeds.
- A comparison of the control market and the signal market.
- A 3 to 5 page report (abstract, introduction, engine architecture, correctness, performance, research method, results, limitations, conclusion) and a 5–7 minute individual demo plus short viva.

**Rules:** never put future data into a feature. Never use the simulator's hidden fair value as a feature.
A null result is fine. Predicting well on synthetic data does not show a real trading edge.
