# Free pre-SDAC price signals and morning issuance feasibility

Accessed and probed: 2026-09-12 to 2026-09-13. Status tags: **V** = verified in first-party documentation or a direct first-party endpoint, **O** = directly observed through a secondary implementation, **I** = inference from verified facts, and **U** = not established.

## Corrected decision

ENTSO-E Transparency Platform A44 is an eligible zero-cost operational source for the separate EXAA 10:15 DE-LU auction curve. **V** The supported A44 REST request can select `classificationSequence_AttributeInstanceComponent.position=2`. **V** The ENTSO-E user interface identifies DE-LU Sequence 1 as SDAC and Sequence 2 as EXAA's separate 10:15 auction. The earlier conclusion that A44 could not distinguish EXAA was wrong because it considered only the usual A44 fields and missed this optional classification-sequence filter.

Use the source under a deliberately narrow contract:

- the 05:30 Europe/Berlin Day-Ahead issuance never uses same-morning EXAA;
- the later D+1 issuance may use only a complete A44 Sequence 2, `PT15M` curve received by its Information Cutoff;
- the system publishes the derived SDAC forecast and source provenance, not the raw EXAA curve;
- absence, lateness, ambiguity, or incompleteness selects a registered no-EXAA fallback instead of delaying issuance or filling values; and
- every poll is retained prospectively so observed latency and revisions can replace schedule-based assumptions.

An 11:30 Europe/Berlin cutoff is feasible but has no recovery margin guaranteed by the source documents. **V** EXAA matching can finish as late as 10:30, and ENTSO-E requires energy prices no later than one hour after the matching-algorithm output time. Therefore 11:30 is the documented outer bound on an ordinary latest-finish day, not an SLA that the curve will always be fetchable earlier. The production workflow should begin polling before 11:30, freeze at 11:30, and fall back immediately if the curve is not complete. Exact issuance and publication deadlines belong to [Choose forecast origins and horizon information sets](https://github.com/bhanuprasanna2001/delu/issues/8).

This is a technical reading of source contracts, not legal advice.

## Exact ENTSO-E contract

### Supported request

The current official ENTSO-E Postman reference lists the classification sequence as an optional Energy Prices request parameter. **V** For a UTC half-open interval covering one DE-LU Market Delivery Day, the request is:

```text
GET https://web-api.tp.entsoe.eu/api
  ?documentType=A44
  &in_Domain=10Y1001A1001A82H
  &out_Domain=10Y1001A1001A82H
  &contract_MarketAgreement.type=A01
  &classificationSequence_AttributeInstanceComponent.position=2
  &periodStart=<yyyyMMddHHmm UTC>
  &periodEnd=<yyyyMMddHHmm UTC>
```

Authentication uses the registered user's ENTSO-E security token. The filter is a request parameter, not merely a value to classify after downloading both sequences. Parameter names should be emitted exactly as documented even though third-party clients demonstrate that the service has tolerated capitalization variants. [Official REST API collection, `12.1.D Energy Prices`](https://documenter.getpostman.com/view/7009892/2s93JtP3F6)

The returned `Publication_MarketDocument` and each `TimeSeries` must still be validated. Persist at least document `mRID`, `revisionNumber`, `createdDateTime`, sender, series `mRID`, in/out domains, contract type, classification sequence, currency, price unit, curve type, period bounds, resolution, point positions, and raw payload checksum. **V** ENTSO-E defines the classification sequence as the relative sequence of a time series where several auctions share an auction category and contract type. [Publication document UML model and schema, TimeSeries table](https://eepublicdownloads.entsoe.eu/clean-documents/EDI/Library/cim_based/schema/Publication_document_UML_model_and_schema_v1.3.pdf)

### Sequence meaning

For `BZN|DE-LU`, the current ENTSO-E user interface states:

- Sequence 1 is the SDAC day-ahead price whose normal gate closure is 12:00 CET/CEST D-1; and
- Sequence 2 is the separate EXAA 10:15 CET/CEST auction price.

The [dynamic ENTSO-E Energy Prices UI](https://newtransparency.entsoe.eu/market/prices/dayAhead/PT15M) is the first-party source. The [`entsoe-py` report that captured the UI wording](https://github.com/EnergieID/entsoe-py/issues/422) is secondary corroboration. Its current raw client also implements the supported A44 query by passing `contract_MarketAgreement.type=A01` and the classification sequence. [`entsoe-py` query implementation](https://github.com/EnergieID/entsoe-py/blob/master/entsoe/entsoe.py)

Do not identify EXAA using arrival order, list index, price differences, or resolution. Select and validate Sequence 2 explicitly. Sequence 1 remains the realised SDAC target.

## Timing and calendar

- **V** EXAA calls the 10:15 Classic Auction an independent first price signal and distinguishes it from its 12:00 SDAC auction. [Trading with EXAA](https://www.exaa.at/en/energytrading/handel-mit-exaa/)
- **V** The official rules do not guarantee matching at exactly 10:15. Pre-trading runs from 08:00 until approximately 10:10 CET, matching can run from 10:00 until 10:30 CET, post-trading can run until 10:40 CET, and EXAA may alter phases in individual cases. There is no post-trading for quarter-hour products. [EXAA Trading Rules, section 4](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** ENTSO-E defines the day-ahead gate-closure timestamp for this publication as the matching-algorithm output time and requires publication no later than one hour afterward. Updates are allowed. The power exchange or TSO is the primary owner and provider. [ENTSO-E Detailed Data Descriptions v3r4, Energy Prices](https://eepublicdownloads.entsoe.eu/clean-documents/Transparency/MoP_Ref2_DDD_v3r4.pdf)
- **I** If EXAA matching ends at its ordinary latest time of 10:30, ENTSO-E's publication deadline is 11:30. Exceptional auction changes, submission failures, platform incidents, or an API response received just after the deadline remain possible.
- **V** EXAA trading days are workdays Monday through Friday except listed non-trading days. When one trading day covers several delivery days, the auctions run separately with a time delay. [EXAA Trading Rules, section 4](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** A direct EXAA page probe on 2026-09-12 returned delivery days through Monday 2026-09-14 and identified Friday 2026-09-11 as the Monday curve's `AuctionDay`. [EXAA public trading-results endpoint](https://www.exaa.at/data/trading-results)

Consequently, Sequence 2 is delivery-day keyed, not always same-morning data. A Saturday, Sunday, Monday, or holiday D+1 forecast may use a curve auctioned on an earlier trading day. Store the auction day where supplied, ENTSO-E document creation time, first-seen time, and signal age. Never substitute the newest curve merely because its delivery day is close.

## Resolution, DST, and market regimes

- **V** EXAA has offered integrated quarter-hour products since 3 September 2014. Its current normal 10:15 auction contains 96 quarter-hours, 24 hours, and blocks. [Trading with EXAA](https://www.exaa.at/en/energytrading/handel-mit-exaa/)
- **V** EXAA's rules define 92 quarter-hours on the spring transition day and 100 on the autumn transition day. [EXAA Trading Rules, annex 1](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** EXAA says German and Austrian auction prices have been calculated separately since the October 2018 zone split. [Trading with EXAA](https://www.exaa.at/en/energytrading/handel-mit-exaa/)
- **V** The ENTSO-E DE-LU bidding-zone EIC is `10Y1001A1001A82H`, applicable from 2018-10-01. The earlier DE/AT/LU EIC is a different market regime and must not be relabeled as DE-LU. [ENTSO-E area and EIC list](https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC)
- **O** Current ENTSO-E Sequence 2 responses contain native `PT15M` EXAA data. The independent `entsoe-py` integration added a local-auction method that selects a sequence and resolution, and current public cache evidence separately exposes a DE-LU Sequence 2 `PT15M` series. These observations corroborate, but do not replace, first-party contracts.

For every requested local delivery date, construct `[local midnight, next local midnight)` in `Europe/Berlin`, convert both ends to UTC for `periodStart` and `periodEnd`, and require exactly 92, 96, or 100 distinct UTC intervals as dictated by that local date. Preserve UTC start as the identifier plus local label and UTC offset. Never manufacture the missing spring hour, merge the repeated autumn hour, or accept four copies of an hourly value as native quarter-hour observations.

The A44 response can contain more than one resolution. The late model's EXAA feature is specifically the Sequence 2 `PT15M` series. Hourly EXAA values and blocks are distinct products and must not be expanded or mixed into that feature.

## Historical availability and point-in-time limits

The semantic earliest possible DE-LU Sequence 2 history is delivery date 2018-10-01 because that is when the DE-LU zone began and EXAA began calculating Germany separately from Austria. **U** First-party documentation does not state the earliest historical date for which ENTSO-E A44 Sequence 2 is actually extractable. Do not turn the semantic boundary into an availability claim.

The evidence establishes:

- **V** the current supported A44 query and Sequence 2 meaning;
- **V** EXAA's native quarter-hour product predates the DE-LU zone;
- **O** public implementation reports show the filter working by 2025 and current live data show it working in 2026; and
- **U** uninterrupted Sequence 2 coverage back to 2018, missing days, corrections, and resolution anomalies have not been measured with an authenticated ENTSO-E backfill.

An authenticated coverage probe is therefore a required data-onboarding acceptance test, not a reason to reject the live source. Query in bounded periods from 2018-10-01 onward and report, by Market Delivery Day: document count, sequence, resolution, expected versus observed interval count, duplicates, currency/unit, document revision and creation time, and missing periods. Keep raw responses. Earlier DE/AT/LU data, if available, remains an explicitly separate auxiliary regime.

ENTSO-E exposes current or corrected delivery-time documents. **V** A44 supports updates, but its request filters delivery time and contains no historical `as_of`, ingestion-time, or first-seen parameter. `revisionNumber` and `createdDateTime` describe the document returned; they do not reconstruct every version that was visible at a historical 11:30 origin. Therefore:

- historical Sequence 2 values can be candidate model features only under a documented schedule-based availability assumption;
- where the returned document creation time is later than the simulated origin, exclude it from that backtest row;
- a no-EXAA late-origin model must be evaluated on the same folds to measure sensitivity to that assumption; and
- strict latency, outage, and revision distributions begin only with prospective immutable polling.

This limitation must remain visible in experiment metadata. A current database value does not prove that the same value was available at 11:30 on its historical publication day.

## Access and reuse boundary

ENTSO-E API access is zero-price but requires registration and a security token. The supported interface is preferable to EXAA's private page JSON and Energy-Charts' chart payload.

The current ENTSO-E Terms of Use permit consulting and using Transparency Platform data subject to good-faith use, source attribution, technical rules, and primary-owner rights. They require users to check the separately maintained free-reuse list before re-use. [ENTSO-E Transparency Platform Terms of Use](https://transparency.entsoe.eu/content/static_content/download?path=%2FStatic+content%2Fterms+and+conditions%2F230309_ENTSOE_Transparency_Terms_Conditions_MC_APPROVED.pdf)

Day-ahead energy prices under Transparency Regulation article 12.1.d are not listed in the published CC BY 4.0 free-reuse list. [List of data available for free re-use](https://transparency.entsoe.eu/content/static_content/Static%20content/terms%20and%20conditions/220218_List_of_Data_available_for_reuse.pdf) That means ENTSO-E access being free does not grant a general CC BY licence to republish raw EXAA prices.

The product contract avoids that unsupported step:

- use Sequence 2 internally as an input to the forecasting calculation;
- publish only the independently generated SDAC point and quantile forecasts;
- disclose `ENTSO-E Transparency Platform, A44, DE-LU, Sequence 2` as input provenance without implying ENTSO-E or EXAA endorsement; and
- do not expose, proxy, download, chart, or redistribute raw Sequence 2 values through the public website or API.

This narrow derived-output use is the production decision. If the product later republishes raw EXAA observations, uses them in a commercial service, or exposes enough data to reconstruct the source curve, obtain written permission from the primary owner first.

## Source eligibility matrix

| Candidate | Result | Role |
| --- | --- | --- |
| ENTSO-E A44 Sequence 2 | Supported, zero-price authenticated API; exact sequence filter; no historical vintage API; raw-price free-reuse licence not established. **V** | Primary operational EXAA input for the later D+1 model under the narrow derived-output contract. |
| Direct EXAA public-page JSON | Current native quarter-hour result but undocumented endpoint, shallow observed history, no service contract, and restrictive database-transmission terms. **V** | Diagnostic cross-check only, not production ingestion. |
| EXAA Trading API | Available to trading participants, not a public-data API. **V** | Ineligible. |
| Wiener Börse EXAA market data | Supported real-time/end-of-day and historical product, but paid. **V** | Ineligible under the zero-cost constraint. |
| Energy-Charts supported API | Bidding-zone SDAC prices copied unchanged from SMARD; no EXAA series in its OpenAPI contract. **V** | Realised SDAC fallback/cross-check, not EXAA. |
| Energy-Charts chart payload | Displays an EXAA item but it is outside the supported API and marked non-downloadable. **V** | Ineligible for automated production use. |
| SMARD | Supported coupled SDAC target after the auction; no separate EXAA curve. **V** | Primary or fallback realised target according to the target-source decision. |
| Netztransparenz | Ex-post monthly market values, not a pre-SDAC price signal. **V** | Ineligible for this feature. |

The earlier EXAA-source audit remains useful for rejecting unsupported direct and Energy-Charts routes. Only the ENTSO-E A44 classification-sequence conclusion changes.

## Minimum production-safe behavior

For the late D+1 issuance:

1. Poll the supported Sequence 2 query before the cutoff and retain every raw response with request, receipt, and ingestion timestamps.
2. At the Information Cutoff, accept only one unambiguous `PT15M`, EUR/MWh, Sequence 2 curve for the exact D+1 UTC interval with the expected 92, 96, or 100 points.
3. If valid, score the EXAA-enabled model and record the source document identity, revision, creation time, first-seen time, checksum, and input profile in forecast provenance.
4. If missing, late, duplicated, wrong-resolution, wrong-day, or incomplete, score the registered no-EXAA fallback. Mark the issuance input profile and degraded reason explicitly. Do not carry forward another delivery day's curve and do not wait beyond the pre-SDAC safety deadline.
5. Never rewrite an issued forecast when A44 is corrected. Store the correction as another source revision and use it only in later training/evaluation decisions unless a new pre-gate issuance is explicitly allowed.

The no-EXAA fallback is not optional. It is the simplest production-safe response to an external signal whose exact historical and tail latency are not recoverable.

## Nonblocking prospective latency monitor

Start the monitor as soon as ingestion work begins, but do not make Wayfinding or the 05:30 product wait for a long observation study.

For each EXAA trading day, poll A44 Sequence 2 at a low fixed cadence from before the expected result until the 11:30 cutoff. For each attempt retain request time, response time, HTTP result, raw checksum, document and revision identifiers, `createdDateTime`, delivery-day coverage, resolution, point count, and validation outcome. Record later revisions through the day. Include Fridays with several delivery days, holidays, both DST transitions, and any delayed auction observed.

Report at least:

- first-seen complete time and minutes from 10:15, matching completion where known, and 11:30;
- completeness rate by delivery-day relationship and calendar class;
- p50, p95, p99, maximum, and after-cutoff frequency;
- revision frequency and time to final observed revision; and
- how often the no-EXAA fallback would have been selected.

Thirty consecutive EXAA trading days are enough for an initial operational check, not an annual-tail SLA. Keep monitoring permanently. Once enough prospective predictions exist, compare the enriched and fallback late models on identical forecast origins before claiming that EXAA improves accuracy.

## Direct probes and corroboration

- The official Postman collection retrieved on 2026-09-13 lists `classificationSequence_AttributeInstanceComponent.position` as an optional `12.1.D Energy Prices` query parameter alongside A44, in/out domain, and A01 day-ahead contract type.
- The official Publication document model defines that element on each `TimeSeries` and explains that it separates several auctions within the same auction category and contract type.
- The first-party ENTSO-E UI mapping of DE-LU Sequence 1 to SDAC and Sequence 2 to EXAA is quoted in the independent `entsoe-py` issue. Its present raw client emits the same supported sequence query parameter.
- A direct 2026-09-12 EXAA page probe returned native quarter-hour DE curves for four delivery days and an `AuctionDay`, but no source publication timestamp.
- The supported Energy-Charts OpenAPI contract retrieved on 2026-09-12 contained no EXAA endpoint or exchange selector. Its DE-LU SDAC series is copied from SMARD.
