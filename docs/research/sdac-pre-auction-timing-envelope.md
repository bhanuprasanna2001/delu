# Genuine DE-LU SDAC pre-auction timing envelope

Accessed: 2026-09-12

## Question

What official SDAC operational timetable constrains a genuine DE-LU day-ahead price forecast, including normal days, clock changes, and exceptional market-coupling paths?

## Decision-ready answer

The routine hard boundary is the NEMO order-book gate closure at **12:00 CET/CEST on trading day D-1**, every calendar day. A forecast described as genuinely pre-auction must both use an information set frozen strictly before that boundary and be issued before it. Current SDAC preliminary results cannot be published before 12:55 CET/CEST, and final results are normally firm around 13:05 but have no fixed publication instant.

Later order-book reopenings under partial or full decoupling do not extend the comparable routine pre-auction envelope. They are exceptional, outcome-dependent processes. The final Forecast Origin remains a product decision. Viable operational buffers to test are 5, 15, and 30 minutes before gate closure.

## Terms used here

- **Trading day D-1**: the local calendar day on which orders close for delivery day D.
- **Gate Closure Time (GCT)**: the last point at which a participant can enter an order in the NEMO trading platform.
- **Information Cutoff**: the latest source-availability timestamp admitted to a forecast's feature set.
- **Forecast Origin**: the product's chosen logical forecast time. This research does not select it.
- **Issued At**: when the completed forecast becomes an immutable official forecast vintage.
- **Preliminary results**: results published after NEMO validation, not yet firm.
- **Final results**: published results confirmed as firm after the final NEMO and TSO validation round.

These concepts must remain separate. In particular, an early Information Cutoff does not make a forecast pre-auction if the forecast itself was only issued after GCT.

## Governing gate closure

Article 47(2) of the CACM Regulation sets day-ahead gate closure in each bidding zone at noon market time on D-1. Article 47(3) requires market participants to submit orders before that time. The current SDAC Fallback Manual expresses all operational times as CET/CEST and places NEMO order-book closure at 12:00. EPEX likewise describes its coupled day-ahead order book as closing at 12:00 on D-1 and the auction as running every day of the year.

Therefore:

```text
information_cutoff_at < 12:00:00 CET/CEST on trading day D-1
issued_at             < 12:00:00 CET/CEST on trading day D-1
```

**Inference:** use a strict inequality. A record stamped exactly `12:00`, especially by a source with only minute precision, is not safely demonstrable as available before closure and should be excluded from a pre-auction replay.

## Current normal-day timetable

All times below are CET/CEST on D-1. The current NEMO manual, published with version 1.3 in May 2026, is the primary operational source for this summary.

| Time | Event | Consequence for forecasting |
|---|---|---|
| 09:30-10:30, latest 11:30 | TSOs make cross-zonal capacities available | Potentially usable only if the particular datum's first-available time is proven and precedes the chosen Information Cutoff. |
| 12:00 | NEMO order books close | Hard end of the routine pre-auction envelope. |
| Not before 12:55 | Preliminary market-coupling results are first published | These contain the target outcome and are forbidden to pre-auction training or inference. |
| Around 13:05 | Final confirmation normally completes | There is deliberately no fixed final-publication instant. |
| 13:50 | Risk-of-full-decoupling message on a severely delayed day | Post-auction operational state, not a pre-auction feature. |
| 14:20 | Latest coupled-results publication or declaration of full decoupling | Exceptional outer limit, not an extension of GCT. |

The preliminary-to-final validation normally takes about ten minutes. The manual says preliminary values do not change when they are successfully confirmed. If preliminary results fail final validation, however, they are cancelled and a fresh calculation and preliminary publication follow.

This creates three distinct boundaries:

1. **Auction participation ends at 12:00.** This determines whether the system was genuinely pre-auction.
2. **The coupling calculation and validations happen after closure.** Their internal inputs and state are not legitimate public predictors.
3. **The first public target-bearing results appear no earlier than 12:55.** This is the obvious target-leakage boundary, but it is too late to define a pre-auction forecast.

**Inference:** even if a public fundamental released at 12:20 contains no direct price result, using it would make the forecast post-auction because it could not have been issued before the order book closed.

## Calendar and daylight-saving semantics

The auction runs once a day, every day of the year. The reviewed first-party materials specify no separate weekend or public-holiday GCT. Operational incidents, not the civil calendar, trigger exceptional paths.

SDAC documents express timings in CET/CEST. EU summer-time rules advance clocks by one hour from 01:00 UTC on the last Sunday in March until 01:00 UTC on the last Sunday in October. For DE-LU, the safe implementation interpretation is:

- winter GCT: `12:00 CET = 11:00 UTC`;
- summer GCT: `12:00 CEST = 10:00 UTC`;
- resolve the offset from the **trading date D-1**, not from the delivery interval and not from a fixed UTC hour.

**Inference:** represent the rule as 12:00 in `Europe/Berlin` on the local trading date, then convert that aware instant to UTC. Do not derive GCT by subtracting 24 hours from a delivery timestamp.

For a delivery day that is the spring clock-change Sunday, D-1 is Saturday while CET is still active, so GCT is 11:00 UTC. For a delivery day that is the autumn clock-change Sunday, D-1 is Saturday while CEST is still active, so GCT is 10:00 UTC. If the trading date itself is the transition Sunday, the offset in force at local noon is used. The 12:00 wall-clock rule itself does not become ambiguous because the clock transition occurs earlier in the day.

## Exceptional paths

Exceptional procedures change result formation and publication, but not the normal 12:00 boundary used for a comparable pre-auction forecast.

### Capacity-related partial decoupling before GCT

If valid cross-zonal capacities are missing, the current manual schedules a risk message at 11:15 and partial decoupling of affected interconnectors at 11:30. Areas and interconnectors that remain coupled retain the normal 12:00 order-book closure and normal result-publication target.

These pre-GCT operational messages may be legitimate inputs only when their actual first-available timestamps are archived. Whether to use them is a separate feature decision.

### Partial decoupling during coupling

For a NEMO/order-book problem during the coupling process, the current timetable has a risk message at 12:35 and a partial-decoupling deadline at 13:00. Order books for areas remaining coupled reopen at 13:05 for 15 minutes; results may then arrive as late as 14:20. A decoupled area follows its local or regional rules.

**Inference:** this reopening must not be treated as a shifted routine GCT. It is conditional on a post-12:00 incident, and bids may be modified after market participants have received operational information unavailable at the original close.

### Full decoupling

If results remain unavailable, risk of full decoupling is announced at 13:50 and full decoupling is declared at 14:20. In the Core region, applicable NEMOs may reopen local order books from 14:28 to 14:38 and target local results by 14:50. Full or partial decoupling known in advance is communicated through a risk message at 10:00 and declaration at 10:30, after which affected areas follow local or regional rules.

**Inference:** a DE-LU local fallback result and a coupled SDAC result need an explicit outcome-status distinction in evaluation. Which one belongs in the target series is outside this timing ticket.

### Delays without decoupling

Preliminary publication may be delayed from 12:55 until 14:20, and final confirmation may be delayed from around 13:05 until 14:20. The coupling can still succeed. A published preliminary result can also be cancelled before a second calculation. Backtests must use the final target revision while retaining the exceptional-session status; no result-publication timestamp may enter the pre-auction feature set.

### Historical second auctions

Historically, price thresholds could trigger a second auction in some bidding zones: order books reopened for 15 minutes and market participants could modify bids after the initial calculation. The 2024 CACM report records that NEMOs decommissioned this process for all bidding zones except the Baltic states on 29 January 2025. DE-LU is therefore no longer subject to this price-threshold second-auction path, but older DE-LU targets may include it.

**Inference:** historical second-auction days remain valid hard forecasting cases for a forecast issued before the original 12:00 GCT, but they should be tagged as a distinct target-formation regime.

## Timetable changes relevant to historical replay

The noon GCT is stable in the reviewed regulatory and EPEX material. Post-close calculation, validation, and fallback deadlines have changed, so those times must be versioned rather than projected backward:

- On 17 June 2021, SDAC increased allowed calculation time. The announced preliminary publication moved from 12:42 to 12:45, the missing-order-book partial-decoupling deadline from 12:40 to 12:45, and the full-decoupling deadline from 13:50 to 14:00.
- With Core flow-based market coupling in June 2022, operational changes moved the partial-decoupling deadline to 13:05 and the full-decoupling deadline to 14:20.
- Before the 15-minute MTU transition, the 2025 joint ENTSO-E report described regular publication at 12:52 and firm confirmation at 12:57. The 15-minute design moved those times to 12:55 and 13:05, moved the partial-decoupling deadline from 13:05 to 13:00, and retained the 14:20 full-decoupling deadline.
- SDAC switched to 15-minute MTUs on trading day 30 September 2025 for delivery on 1 October 2025. EPEX explicitly retained the coupled auction at 12:00 CET/CEST.
- Price-threshold second auctions were decommissioned for DE-LU on 29 January 2025.

No reviewed primary source announces a change to the 12:00 CET/CEST gate closure as of the access date. Official pages warn that operational documents can be amended, replaced, or withdrawn. Production should therefore monitor and version the current NEMO/ENTSO-E timetable rather than treating post-close deadlines as timeless constants.

## Candidate safety margins

The regulation establishes the boundary, not a suitable production margin. The margin must cover scheduler jitter, source polling, ingestion completion, point-in-time feature materialisation, inference, persistence, publication, clock skew, and at least the intended retry policy.

**Inferred candidates for measurement, not a selected Forecast Origin:**

| Candidate issue deadline | Gate buffer | Trade-off to test |
|---|---:|---|
| 11:55 CET/CEST | 5 minutes | Maximises freshness but leaves little room for queueing or retry. Viable only if measured end-to-end tail latency is comfortably below the buffer. |
| 11:45 CET/CEST | 15 minutes | Allows modest operational variance and a short retry while retaining relatively fresh inputs. |
| 11:30 CET/CEST | 30 minutes | Provides stronger contingency but excludes later pre-GCT source updates and some operational messages. |

For any candidate issue deadline `I`, choose the Information Cutoff `C` so that:

```text
C + measured_p99(end-to-end build and issue latency) + retry/clock contingency <= I < GCT
```

Selection requires measured Databricks job-start and processing latency plus the feature-availability matrix. This ticket does not choose among the candidates.

## Requirements carried into the specification

1. Compute GCT from the Europe/Berlin local trading date, store the resolved UTC instant and offset, and never hardcode one UTC hour year-round.
2. Persist Information Cutoff, Forecast Origin, Generated At, and Issued At separately.
3. Reject any official pre-auction issuance with `issued_at >= gct_at`.
4. Admit only feature revisions proven available at or before the chosen cutoff. Treat an availability timestamp equal to GCT or coarser than the necessary proof boundary as unsafe.
5. Preserve auction/session status: normal coupled, delayed, partial decoupling, full decoupling/local fallback, historical second auction, and result revision/cancellation.
6. Version the market timetable by effective trading date and retain the primary notice used for each version.
7. Alert on any official change to GCT, time-zone convention, or fallback schedule before it becomes effective.

## Sources

All sources were accessed 2026-09-12.

- European Commission, [Commission Regulation (EU) 2015/1222, Article 47](https://eur-lex.europa.eu/eli/reg/2015/1222/oj). Primary regulatory definition of noon market-time GCT and the requirement to submit orders before it.
- NEMO Committee, [SDAC Fallback Manual v1.2 and v1.3](https://www.nemo-committee.eu/assets/files/sdac-fallback-manual-v12-and-v13.pdf). Current normal, delayed, partial-decoupling, full-decoupling, and CET/CEST timetable.
- ENTSO-E, [SDAC Fallback Manual](https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Network%20codes%20documents/NC%20CACM/SDAC%202025/SDAC_Fallback_Manual.pdf). ENTSO-E-hosted copy of the operational manual.
- EPEX SPOT, [Trading Brochure, February 2025](https://www.epexspot.com/sites/default/files/2025-02/EPEX%20SPOT%20Trading%20Brochure%202025%20February.pdf). First-party confirmation of daily operation, D-1 12:00 order-book closure, and the pre-15-minute result-publication target.
- EPEX SPOT, [15-minute products in Market Coupling](https://www.epexspot.com/en/new-15-minute-products-market-coupling). First-party confirmation that the 15-minute transition retained the 12:00 coupled auction and took effect on trading day 30 September 2025 for delivery on 1 October 2025.
- ENTSO-E, [Single Day-ahead Coupling implementation page](https://www.entsoe.eu/network_codes/cacm/implementation/sdac/). Current official SDAC status, documents, press releases, and change notices.
- ENTSO-E and GB transmission owners, [Joint report on Multi-Region Loose Volume Coupling](https://eepublicdownloads.blob.core.windows.net/public-cdn-container/clean-documents/Reports/2025/MRLVC_Report.pdf). Primary joint account of pre- and post-15-minute operational timings.
- NEMO Committee, [26 May 2021 communication note on new timings](https://www.nemo-committee.eu/assets/files/sdac-communicaton-note-on-new-timings.pdf). Primary announcement of the 17 June 2021 calculation and fallback changes.
- Market Coupling Steering Committee, [25 February 2022 letter to national regulatory authorities](https://www.raaey.gr/energeia/wp-content/uploads/2022/03/1_220225-MCSC-letter-NRAs-re.-pending-approvals-changing-SDAC-decoupling-deadlines.pdf). Primary request and rationale for moving the partial- and full-decoupling deadlines to 13:05 and 14:20 with the Core flow-based changes.
- ENTSO-E and NEMOs, [CACM Cost Report 2024](https://eepublicdownloads.entsoe.eu/clean-documents/nc-tasks/2024_CACM_cost_report.pdf). Primary record of second-auction decommissioning.
- European Union, [Directive 2000/84/EC on summer-time arrangements](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32000L0084). Primary rule for EU clock-change instants.
- NEMO Committee, [report on the partial decoupling incident of 28 October 2023](https://www.nemo-committee.eu/assets/files/sdac-report-on-the-partial-decoupling-incident-of-october-28th-2023-.pdf). Primary evidence that a long clock-change delivery day can interact with exceptional validation and delayed publication.
