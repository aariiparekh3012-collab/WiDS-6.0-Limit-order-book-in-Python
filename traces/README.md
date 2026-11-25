# Active golden traces

The manifest is the authoritative inventory: three Foundation traces, four Advanced traces and two optional Cancel Newest traces.

| Tier | Active trace names |
| --- | --- |
| 1 | t1_basic, t1_fuzz_s1, t1_fuzz_s2 |
| 2 | t2_fuzz_s3, t2_fuzz_s4, t2_ioc_fok, t2_modify |
| 3 (optional) | t3_stp_newest (input t3_stp.csv), t3_newest_fok_atomic |

The CSV inputs and expected JSONL outputs are regression fixtures for the [educational specification](../docs/SPECIFICATION.md). Do not modify them. Historical, ungraded STP fuzz, Cancel Oldest/Cancel Both and C++ compatibility fixtures were removed from the active directory; they can be recovered from Git history at commit eb5b965. No active fixture or manifest entry was changed.
