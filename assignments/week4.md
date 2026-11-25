# Week 4: Quantitative research

**Question:** can depth imbalance and order-flow imbalance (OFI) predict short-term mid-price changes in a simulated market? Keep contemporaneous price impact separate from out-of-sample predictability.

Individual assignment. The Week 4 kit in `research/` has an agent-based simulator (liquidity providers, noise traders, informed traders), a recorder and a notebook template in `notebooks/`. Run control and signal configurations through your own engine. NumPy, pandas, Matplotlib and scikit-learn permitted; logistic regression compulsory, Random Forest optional. Handle empty or crossed snapshots explicitly, preserve original command indices when constructing the target.

**Hand in**
- A reproducible generator setting: seed and configuration.
- Data quality summary, class counts and feature plots.
- Features: spread, mid-price, depth imbalance, OFI, signed trade volume, rolling volatility and lagged returns.
- Target: `sign(mid[t+10] - mid[t])`, ten command observations ahead. Classes: down (-1), unchanged (0), up (+1).
- A chronological split inside each sequence (60% train, 20% validation, 20% test), labels purged near the boundaries, preprocessing fitted on train only.
- Models: majority-class baseline, an imbalance-threshold rule, and logistic regression.
- Metrics: accuracy, balanced accuracy, macro F1, confusion matrix, comparison with baselines, stability across seeds.
- A comparison of the control market and the signal market.
- A concise project report or detailed README summarising engine design, correctness, benchmarking, research method, results and limitations, with reproducibility instructions.

**Rules:** never put future data into a feature. Never use the simulator's hidden fair value as a feature.
A null result is fine. Predicting well on synthetic data does not show a real trading edge.

**Kit commands**
```bash
pip install -r requirements-research.txt
python -m research.make_tapes
python -m research.check_replay          # must say PASSED before you trust your results
python -m unittest research.test_features -v
```
`check_replay` is the automated engine correctness gate on new data; the feature unit tests are implementation self-checks. Research quality, model evaluation and interpretation are reviewed with your mentor.
