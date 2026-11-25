# Learning resources

All four weekly guides contain concept explanations, worked examples, exercises, practical tasks and completion checklists. Start from the [Notion curriculum](https://app.notion.com/p/4233d7dedf7481cfbd3cf9bd47feef69).

## Week 1 — Foundation
- [Learning guide](https://app.notion.com/p/4233d7dedf748165b366c72ce4dd52e8) and [assignment](../assignments/week1.md)
- [Matching specification](SPECIFICATION.md), [Python design guide](DESIGN.md), [Book API](../lob/book.py)
- [Readable CSV trace](../traces/t1_basic.csv) and [expected events](../traces/t1_basic.jsonl)
- [Limit Order Books](https://medium.com/reactivemarkets/limit-order-books-9d48adf2c517), [WK Selph on data structures](https://gist.github.com/halfelf/db1ae032dc34278968f8bf31ee999a25)
- Checkpoint: `python grade.py --tier 1` (3/3)

## Week 2 — Advanced engine
- [Learning guide](https://app.notion.com/p/4233d7dedf748115b488e54b3f786c37) and [assignment](../assignments/week2.md)
- [IOC/FOK trace](../traces/t2_ioc_fok.csv), [modify trace](../traces/t2_modify.csv)
- [unittest documentation](https://docs.python.org/3/library/unittest.html), [example tests](../tests/test_book.py)
- Checkpoint: tier 1 and tier 2, seven cumulative traces and five independent tests

## Week 3 — Performance
- [Learning guide](https://app.notion.com/p/4233d7dedf7481e7b400f589fb05559b) and [assignment](../assignments/week3.md)
- [Benchmark script](../bench.py), [recording template](../templates/benchmark.csv)
- [cProfile](https://docs.python.org/3/library/profile.html), [perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter)
- Choose Basic or Intermediate; preserve mandatory correctness. Cancel Newest is optional.

## Week 4 — Quantitative research
- [Learning guide](https://app.notion.com/p/4233d7dedf7481c19fdad5625b0c82b4) and [assignment](../assignments/week4.md)
- [Cont, Kukanov & Stoikov: The Price Impact of Order Book Events](https://arxiv.org/abs/1011.6402)
- [pandas](https://pandas.pydata.org/docs/getting_started/index.html), [logistic regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- Simulator and notebook template supplied during Week 4. Submit your reproducible notebook and [concise project summary or README](../templates/report.md).
