# DE-LU SDAC target history and regime boundaries

Research completed 2026-09-12 for the Wayfinder ticket [Verify SDAC target history and regime boundaries](https://github.com/bhanuprasanna2001/delu/issues/2).

## Decision

Use three explicitly different label regimes. Never coerce either hourly regime into observed quarter-hour labels.

| Delivery interval | Bidding zone | ENTSO-E EIC | Source-native price resolution | Permitted ML role |
| --- | --- | --- | --- | --- |
| 2018-01-01 through 2018-09-30 | DE/AT/LU | `10Y1001A1001A63L` | 60 minutes | Optional auxiliary or transfer data only, with a distinct regime identifier. Do not treat it as the DE/LU target. |
| 2018-10-01 through 2025-09-30 | DE/LU | `10Y1001A1001A82H` | 60 minutes | Auxiliary hourly supervision for a multi-resolution experiment. Do not repeat each value four times as quarter-hour truth. |
| From 2025-10-01 | DE/LU | `10Y1001A1001A82H` | 15 minutes | Canonical observed target for training, validation, backtesting and realised forecast evaluation. |

The production output can always have 15-minute delivery intervals, but only the final regime contains observed 15-minute clearing-price labels. The modeling decision must be made by a leakage-safe empirical comparison whose primary validation period contains native 15-minute labels. At minimum, compare a native-15-minute-only model with models that use the older regimes through an auxiliary hourly loss, transfer learning, an hourly-level plus learned quarter-hour deviation decomposition, or an ensemble. Old hourly observations cannot measure historical within-hour shape and therefore cannot validate it.

SMARD is the preferred redistributable target feed. Direct ENTSO-E A44 is useful as upstream lineage and an operational cross-check, subject to separate legal review before redistributing it. The two feeds are not independent observations: SMARD says it retrieves the data automatically from ENTSO-E, validates it, and republishes it.

## Verified boundaries

### Bidding zone

The Bundesnetzagentur's 2018 monitoring report says that the joint German-Austrian market area was split on 1 October 2018 and that the former zone left a Germany/Luxembourg zone and a separate Austrian zone. The current SMARD guide likewise lists Germany/Luxembourg from 1 October 2018 and Germany/Austria/Luxembourg through 30 September 2018.

ENTSO-E's maintained area list identifies `10Y1001A1001A63L` as `BZN|DE-AT-LU` and `10Y1001A1001A82H` as `BZN|DE-LU`. These EICs, not a country code or display label, are the source identities that should be retained.

### Market Time Unit

ENTSO-E records that SDAC transitioned from hourly to 15-minute Market Time Units in September 2025. Its dated go-live notice specifies trading day 30 September 2025 for delivery day 1 October 2025. EPEX states the same boundary and adds that the clearing-price index itself switched to 15-minute resolution; its 60-minute index thereafter is the arithmetic average of the four quarter-hour clearing prices.

The boundary is therefore based on the delivery interval:

- Last native hourly delivery interval: 2025-09-30 23:00 to 2025-10-01 00:00 Europe/Berlin.
- First native quarter-hour delivery interval: 2025-10-01 00:00 to 00:15 Europe/Berlin.

Do not use the phrase "first trading day 1 October" as a database boundary. Some later EPEX editorial wording uses it, but the contemporaneous MCSC and EPEX implementation pages unambiguously identify 30 September as the trading day and 1 October as the delivery day.

## First-party SMARD probe

On 2026-09-12, a SMARD download was requested at quarter-hour display resolution for 2018-01-01 through 2026-09-13. The response was a 15,617,873-byte UTF-8 CSV named `Day-ahead_prices_201801010000_202609132359_Quarterhour.csv`. Its SHA-256 is `a264daa5edecbff72ef3863bff47962d91872e42b3460c8c6f85af74616c298f`.

The present-day snapshot contained:

| Series and range | Rendered rows with values | Native labels represented | Internal blanks between first and last value |
| --- | ---: | ---: | ---: |
| DE/AT/LU, 2018-01-01 through 2018-09-30 | 26,204 | 6,551 hourly labels | 0 |
| DE/LU, 2018-10-01 through 2025-09-30 | 245,472 | 61,368 hourly labels | 0 |
| DE/LU, 2025-10-01 through 2026-09-12 | 33,312 | 33,312 quarter-hour labels | 0 |

Every group of four rendered rows in each pre-2025-10-01 hour had the same price. Immediately at 2025-10-01 00:00, the four values became `102.60`, `92.24`, `86.03`, and `85.39` EUR/MWh. Across complete local-clock hour groups in the native quarter-hour regime, 8,308 had varying values and 18 happened to be constant. This establishes that the earlier quarter-hour rows are a rendering of an hourly label, while the later rows are native quarter-hour observations.

The row count also preserves clock changes. A spring transition date has 92 rows, a normal date 96, and an autumn transition date 100. The autumn export repeats the local 02:00 labels without an offset, so the displayed local timestamp alone is ambiguous. Ingestion must assign a UTC interval and offset in source order before using the data as a key.

This probe proves current snapshot completeness only. It is not evidence that values were complete or identical at their original publication times. The response window extended through 2026-09-13 but its final populated interval was 2026-09-12 23:45, so even a current download must be checked for freshness rather than assumed complete.

## Availability, correction and vintage behavior

| Property | Verified behavior | Consequence |
| --- | --- | --- |
| Unit | EUR/MWh for each market time unit | Store the source unit and normalized unit even when identical. |
| Source timing | ENTSO-E requires energy prices no later than one hour after gate closure, where gate closure for implicit allocation means matching-algorithm output time. SMARD's public legend says delivery no later than two hours after trading closes. | These prices are realised labels, not legal pre-auction predictors. Track first-seen source availability independently of the regulatory deadline. |
| Updates | ENTSO-E marks Energy Prices 12.1.d as updateable. SMARD permits later price updates and says there is no fixed general revision process. It may replace preliminary values or close historical gaps. | Keep each acquired payload and its ingestion time. Silver must not destructively overwrite revisions. |
| Historical vintages | The ordinary SMARD download and ENTSO-E query return the current view; neither provides an as-published-at timestamp selector for this series in the documented interfaces reviewed. | Historical first-seen availability cannot be reconstructed from the final snapshot. Capture it prospectively. |
| Missing data | The 2026-09-12 snapshot had no internal blanks in the scoped realised ranges. This does not imply uninterrupted historical availability. SMARD documented that wholesale prices disappeared for several days in March 2026 because of an ENTSO-E reporting-chain problem and were later uploaded. | Maintain completeness and staleness checks, revision history and an incident table. Never silently impute the target. |
| Access reliability | SMARD exposes a free download center but no availability SLA was found. ENTSO-E promises best efforts for 24/7 platform availability and reserves the right to impose technical limits on automated extraction. | Cache immutable Bronze payloads and make ingestion idempotent and retryable. Do not make either public web service the website's synchronous dependency. |

SMARD says its data provision begins in 2015, so older DE/AT/LU prices can be downloaded. For this project, 2018-01-01 is the earliest useful candidate because it matches the requested study window. More pre-split years would enlarge the wrong-zone regime without providing any native DE/LU or quarter-hour labels and should be admitted only if an ablation demonstrates benefit.

## Multi-NEMO and decoupling exceptions

An ENTSO-E A44 day-ahead-price request selects a bidding zone and time interval. The extraction guide marks process type, auction type, business type and contract type as unused for this data item, so the documented request cannot select a NEMO. That normally causes no issue because coupled NEMOs share the bidding-zone clearing price. It becomes material when one NEMO's order book is decoupled and a local auction produces another price.

Seed the target-quality incident registry with at least these delivery dates:

| Delivery date | Primary-source finding | Target treatment |
| --- | --- | --- |
| 2019-06-08 | An EPEX problem caused CWE and EPEX GB partial decoupling. EPEX ran local national auctions, first published erroneous partial-order-book results, then recalculated final results at 15:38. | Flag as a decoupling and late-correction day. Verify the exact source price before training. |
| 2020-02-05 | Nord Pool's CWE order book was decoupled while the remaining MRC coupling ran; final coupled results were published at 13:55 CET. | Flag as a multi-NEMO decoupling day and verify which price the target source retained. |
| 2021-01-14 | EXAA was among the NEMOs decoupled following a GME incident, and decoupled markets could run local auctions. | Flag as a multi-NEMO decoupling day and verify which price the target source retained. |
| 2024-06-26 | EPEX's Core order book was decoupled. SMARD explicitly says ENTSO-E supplied only the German prices of unaffected EXAA and Nord Pool, so SMARD does not show EPEX's unusually high local prices. ACER later confirmed that the decoupled EPEX price differed from the SDAC price. | For the stated target, retain the coupled SDAC price but set `market_coupling_status=partial_decoupling`, record the source lineage, and do not describe it as the unique German exchange price. |

These flags are not optional outlier deletion. They describe different clearing circumstances. The modeling evaluation can later decide whether to retain, exclude, down-weight or separately score them, but the raw and normalized records must preserve them.

For a day with multiple NEMO prices, the canonical target remains the coupled DE/LU SDAC price, not a decoupled local exchange price. A historical row whose free source cannot prove that identity must be marked disputed and excluded from supervised scoring until adjudicated. It may still be displayed with its literal source label and incident disclosure. This conservative rule avoids silently changing the target definition for a handful of extreme days.

Other structural breaks should also be explicit covariates, not hidden in a continuous date index. In particular, Core flow-based day-ahead market coupling went live on trading day 8 June 2022 for delivery on 9 June 2022. The harmonised SDAC maximum clearing price changed to +4,000 EUR/MWh from trading day 10 May 2022. The minimum changed to -600 EUR/MWh from trading day 28 May 2026. These changes alter price formation or support and warrant regime metadata even though they do not change the target's identity.

## Required normalized target fields

The eventual Silver contract needs, at minimum:

- `delivery_start_utc` and `delivery_end_utc` as the interval identity
- `delivery_timezone = Europe/Berlin`, local delivery date and local start time for display
- `utc_offset_minutes` and a repeated-interval discriminator
- `mtu_minutes` and `source_native_resolution_minutes`
- `price_eur_per_mwh`
- `bidding_zone_eic` and stable regime identifier
- `source_system`, upstream lineage and source record identifier where available
- `source_publication_time` when supplied, otherwise null plus a documented availability rule
- `first_seen_at`, `ingested_at`, payload checksum and revision sequence
- `market_coupling_status`, `nemo_scope` and incident reference
- target quality state such as observed, missing, corrected or disputed

Bronze must retain the exact response and request metadata. A corrected value creates a new Silver revision; it must not erase what the system previously knew. Gold training may use the latest adjudicated realised price as a label, while point-in-time feature joins remain bounded by the forecast origin. This distinction prevents label correction from being confused with predictor leakage.

## Licensing and redistribution

SMARD is suitable for the public product under the verified terms. The Bundesnetzagentur states that SMARD market data are under CC BY 4.0 and may be downloaded, stored, shared and adapted with attribution to `Bundesnetzagentur | SMARD.de`, a license link and an indication of modifications.

Do not assume that direct ENTSO-E day-ahead prices carry the same permission. ENTSO-E's terms grant CC BY 4.0 only to the items on its published free-reuse list and require users to check that list. The 18 October 2023 list does not include Article 12.1.d day-ahead energy prices. Since exchanges are identified as primary owners, direct A44 redistribution and derived-product rights require confirmation before direct ENTSO-E price data are exposed publicly. This does not affect redistribution of the SMARD copy under SMARD's explicit CC BY 4.0 grant.

## Primary sources

- [Bundesnetzagentur Monitoring Report 2018](https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Downloads/EN/Areas/ElectricityGas/CollectionCompanySpecificData/Monitoring/monitoringreport2018.pdf), especially page 216 and footnote 71.
- [SMARD Benutzerhandbuch, current version landing page](https://www.smard.de/home/benutzerhandbuch), especially sections B.1.3, B.1.4, B.3 and D.3.1 in the September 2026 version.
- [SMARD market-data download and license page](https://www.smard.de/home/downloadcenter/download-marktdaten).
- [SMARD March 2026 wholesale-price data-gap notice](https://www.smard.de/en/update-smard-data-gaps-219614).
- [ENTSO-E area and EIC list](https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC).
- [ENTSO-E Energy Prices 12.1.d data-item specification](https://transparencyplatform.zendesk.com/hc/en-us/articles/16647234190100-Energy-Prices-12-1-D).
- [ENTSO-E Transparency Platform data-extraction implementation guide](https://transparency.entsoe.eu/content/static_content/download?path=%2FStatic+content%2Fweb+api%2FIG-for-TP-data-extraction-process.pdf), day-ahead prices in Table 3.
- [ENTSO-E SDAC implementation and source-document index](https://www.entsoe.eu/network_codes/cacm/implementation/sdac/).
- [EPEX 15-minute products in market coupling](https://www.epexspot.com/en/new-15-minute-products-market-coupling).
- [ENTSO-E Core flow-based go-live announcement](https://eepublicdownloads.entsoe.eu/clean-documents/Network%20codes%20documents/NC%20CCR%20Regions/2022/Core_FB_MC_Announcement_new_go-live_date.pdf).
- [ENTSO-E 2019 EPEX partial-decoupling investigation](https://eepublicdownloads.entsoe.eu/clean-documents/Network%20codes%20documents/Implementation/stakeholder_committees/MESC/2019-09-17/190917_5.5_SDAC%20decoupling%20incident%2007.06_final.pdf?Web=1).
- [ENTSO-E Market Report 2020](https://eepublicdownloads.entsoe.eu/clean-documents/Publications/Market%20Committee%20publications/ENTSO-E_Market_Report_2020.pdf), page 41 for the February 2020 partial decoupling.
- [ENTSO-E Market Report 2021](https://eepublicdownloads.entsoe.eu/clean-documents/nc-tasks/ENTSO_E_Market_report_2021_2e499deda8.pdf), page 53 for the January 2021 partial decoupling.
- [MCSC June 2024 partial-decoupling notice](https://eepublicdownloads.entsoe.eu/clean-documents/mc-documents/market%20coupling/In-depth_Investigation__25-06-2024_.pdf).
- [ACER Decision 08-2025 consultation evaluation](https://eepublicdownloads.entsoe.eu/clean-documents/nc-tasks/ACER%E2%80%99s%20decision%20final%20approval%20%E2%80%93%20Annex%20II%20Evaluation%20of%20responses%202025.pdf), pages 3 to 4.
- [ENTSO-E Transparency Platform terms](https://transparency.entsoe.eu/content/static_content/download?path=%2FStatic+content%2Fterms+and+conditions%2F231018_Terms+and+Conditions_of_Use.pdf), sections 2.5, 3.1, 3.3 and 5.4.
- [ENTSO-E list of data available for free reuse](https://transparency.entsoe.eu/content/static_content/download?path=%2FStatic+content%2Fterms+and+conditions%2F231018_List_of_Data_available_for_reuse.pdf).
