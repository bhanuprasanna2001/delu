# Free pre-SDAC price signals and morning issuance feasibility

Accessed and probed: 2026-09-12. Status tags: **V** = verified in first-party documentation or a direct first-party endpoint probe, **I** = inference from verified facts, **U** = unknown or not contractually established.

## Decision

No eligible zero-cost production source for the EXAA 10:15 DE-LU curve was verified. **V** EXAA produces a real earlier price signal and its public website currently renders the 15-minute result. However, every machine-readable route fails at least one mandatory gate:

- the documented EXAA market-data route is a paid subscription sold by Wiener Börse;
- the EXAA Trading API is for trading participants, not a public data API;
- the JSON used by EXAA's public page is undocumented, retains only four current delivery days in the observed response, has no publication timestamp or service commitment, and has no permission for automated reuse or derived public forecasts;
- Energy-Charts exposes EXAA only in an undocumented chart file whose item is explicitly marked non-downloadable, while its supported API has no EXAA series; and
- ENTSO-E and SMARD expose the coupled bidding-zone day-ahead price after SDAC, not an exchange-distinguishable 10:15 curve before the noon gate.

Therefore the initial production contract must **not** promise an EXAA-enriched 11:30 issuance. **I** It may still define a later pre-SDAC update using other eligible features. Exact origins belong to [Choose forecast origins and horizon information sets](https://github.com/bhanuprasanna2001/delu/issues/8), after the fundamentals and weather audits close.

EXAA can become a candidate later only after both of these gates pass:

1. written permission confirms zero-cost automated use for this non-commercial public informational service, including use as a model input and publication of derived forecasts; and
2. a prospective first-seen study establishes availability, completeness, calendar behavior, and latency at the intended cutoff while creating the historical snapshot ledger that public sources do not provide.

This is a technical reading of published contracts and endpoint behavior, not legal advice.

## What the 10:15 auction actually guarantees

- **V** EXAA describes its independent 10:15 Classic Auction as the first price signal of the day and distinguishes it from its 12:00 SDAC market-coupling auction. A normal 10:15 delivery day has 24 hourly and 96 quarter-hourly products plus blocks. The rules separately define 23 hours and 92 quarter-hours for spring DST and 25 hours and 100 quarter-hours for autumn DST. [Trading with EXAA](https://www.exaa.at/en/energytrading/handel-mit-exaa/), [EXAA Trading Rules, annex 1](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** The official rules do not guarantee a result at exactly 10:15. Pre-trading runs from 08:00 until approximately 10:10 CET, matching may run from 10:00 until 10:30 CET, and post-trading may run until 10:40 CET. There is no post-trading for quarter-hour products. EXAA may change phases in individual cases. [EXAA Trading Rules, section 4](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** The 10:15 exchange calendar is not a simple 365-day calendar. Trading days are workdays Monday to Friday excluding listed non-trading days, and when several delivery days are traded on one trading day, separate auctions are held with a time delay. [EXAA Trading Rules, section 4](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)
- **V** A direct 2026-09-12 probe of the public page's internal endpoint returned delivery days 2026-09-11 through 2026-09-14. The Monday delivery curve identified Friday 2026-09-11 as its auction day. The DE unknown-origin result contained 96 quarter-hour products. [Public trading-results endpoint](https://www.exaa.at/data/trading-results)
- **V** EXAA calls this source region `DE` and defines its "Bidding Zone Germany" using the four German TSO control areas. Energy-Charts instead labels its chart item `Day Ahead Auction EXAA (DE-LU)`. No first-party statement was found that explains this relabeling. A future integration must preserve EXAA's source-native region and obtain written confirmation of its bidding-zone semantics instead of silently treating the two labels as interchangeable. [EXAA Trading Rules, section 11](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf)

The weekend result means that even a permitted feed would not be a uniform daily feature. **I** Training and inference would need the EXAA auction timestamp, delivery day, result first-seen time, signal age, product type, and completeness. On weekends and holidays, the curve for D+1 can be one or more days old even though it was auctioned specifically for that delivery day.

## Source eligibility matrix

| Candidate | What is actually exposed | Timing | History and vintages | Automation and reuse | Classification |
| --- | --- | --- | --- | --- | --- |
| EXAA public results page | Current DE 10:15 prices for hours, blocks, and 96 quarter-hours via `/data/trading-results`; four delivery days in the observed response. **V** | Auction matching can finish as late as 10:30 CET; public-page first-seen latency is **U**. Responses contain `AuctionDay` but no published-at or first-available timestamp. | Four delivery days observed; no supported archive or historical vintages. **V** | The endpoint is called by EXAA's page JavaScript but is undocumented as a public API. [Current EXAA rules](https://www.exaa.at/site/assets/files/1/3_04_trading_rules_spot_market_products_electric_power_per_01_01_2026.pdf) describe the trading database as protected and prohibit electronic transmission to third parties without consent, subject to stated exceptions. **V** | Unusable for production or backtesting without written permission and observation. |
| EXAA Trading API | Automated order and result management for the 10:15 and 12:00 auctions. **V** | Member trading-system timing. | Not documented as a public historical archive. | Available at no additional API fee only to EXAA trading participants. It is not a zero-cost public-data route. **V** [Trading API](https://www.exaa.at/en/marketdata/trading-api/) | Ineligible. |
| EXAA or Wiener Börse market-data service | Real-time and end-of-day 10:15 and 12:00 prices, volumes, and curves over sFTP. **V** | Product-dependent. | The 10:15 package includes current-year history; older history is available on request. **V** | Wiener Börse defines processing and third-party derived data as non-display use. Its price list effective 2026-01-01 charges EUR 550/month for real-time or EUR 250/month for end-of-day 10:15 prices and volumes for Austria and Germany. **V** [EXAA market-data page](https://www.exaa.at/en/marketdata/historical-marketdata/), [Wiener Börse product and use terms](https://www.wienerborse.at/en/market-data/market-data-sales/partner-exchanges-products/exaa/), [2026 price list](https://www.wienerborse.at/uploads/u/cms/files/market-data/en-annex1-market-data-agreement-2026.pdf) | Ineligible under the zero-cost constraint. |
| Energy-Charts supported API | `/price`, `/v2/price`, `/v2/price_current`, and `/v2/price_next_day`; price requests accept a bidding zone, not an exchange or auction. No EXAA identifier occurs in the OpenAPI contract. **V** | The next-day endpoint describes normal availability in the early afternoon, after SDAC. **V** | Historical coupled prices, not historical EXAA vintages. | DE-LU price is copied unchanged from SMARD and explicitly CC BY 4.0. `/price` permits 2 requests/minute with burst 2, v2 inherits the v1 limit, and effective limits may be lower under load. **V** [OpenAPI contract](https://api.energy-charts.info/openapi.json) | Eligible for the realised SDAC target or fallback, not as a pre-SDAC EXAA signal. |
| Energy-Charts static chart JSON | A weekly `Day Ahead Auction EXAA (DE-LU)` array is visible at a static chart path. A 2026-W37 probe returned 672 quarter-hour cells. **V** | No per-series published-at timestamp. File `Last-Modified` reflects whole-file regeneration and does not prove auction-result latency. | Weekly chart files are visible, but no supported archive or vintage contract was found. | Unsupported by the OpenAPI contract. The item has `allowCsvDownloadForItem: false`; the site's publishing notes allow download or print for personal use only unless written approval is obtained. **V** [chart](https://www.energy-charts.info/charts/price_spot_market/chart.htm?l=en&c=DE), [publishing notes](https://www.energy-charts.info/publishing-notes.html?c=DE&l=en) | Ineligible without written permission and a supported contract. |
| ENTSO-E Transparency Platform A44 | One day-ahead energy-price document per bidding zone and MTU. **V** | Publication no later than one hour after gate closure, which ENTSO-E defines as the matching-algorithm output time. This is post-SDAC for the coupled price. **V** | Current/corrected delivery-time series; no as-of price-vintage extraction was established. | A44 request fields use the same in/out domain and do not use process, auction, business, or market-agreement selectors. It cannot request EXAA 10:15 separately. **V** [API extraction guide](https://transparency.entsoe.eu/content/static_content/download?path=%2FStatic+content%2Fweb+api%2FIG-for-TP-data-extraction-process.pdf), [current Manual of Procedures](https://www.entsoe.eu/data/transparency-platform/mop/) | Not a pre-SDAC signal. |
| SMARD wholesale price | Coupled day-ahead bidding-zone price copied through ENTSO-E; primary owners are the exchanges. **V** | Published no later than one hour after bid-acceptance closure according to the current handbook. This is post-auction. | Corrected history may be updated later; no source publication timestamp per value. | Supported public download and useful for the target, but no distinct EXAA auction. [SMARD handbook](https://www.smard.de/resource/blob/220052/9d526adf4b948599da4a956dfae6dab9/smard-benutzerhandbuch-04-2026-data.pdf) | Not a pre-SDAC signal. |
| Netztransparenz | Monthly market values and legally defined volume-weighted spot prices across exchanges. **V** | Published in the following month, not before the SDAC gate. | Ex-post monthly products. | Supported downloads where offered, but no current 10:15 EXAA price feed was found. [Spot price under section 3 no. 42a EEG](https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/EEG/Transparenzanforderungen/Marktpr%C3%A4mie/Spotmarktpreis-nach-3-Nr-42a-EEG) | Not a pre-SDAC signal. |

No other zero-cost, supported, exchange-distinguishable pre-SDAC price feed was verified. **U** Absence from this search is not proof that none can ever exist, but it is sufficient to reject a production dependency until a supported source is identified.

## Energy-Charts is not a free EXAA API

The public website and the supported API have materially different contracts:

- **V** The OpenAPI schema contains only bidding-zone day-ahead price endpoints. It has no exchange parameter and no `EXAA` series. For DE-LU, it says the price data comes from SMARD, is published unchanged, and carries CC BY 4.0.
- **V** The website's private chart payload contains a separate EXAA curve, but that item disables CSV download. Other public series in the same payload, including the coupled DE-LU auction curve, enable it.
- **V** The general publishing notes restrict site material to personal use absent approval. The supported API supplies its own explicit data-licence statements, but the static EXAA chart payload does not.
- **U** No first-party statement was found saying that Energy-Charts receives EXAA directly, may sublicense the result, exposes it by 11:30, or preserves publication-time vintages.

It is therefore unsafe to infer a production licence, lineage, or latency commitment merely because the browser can render the curve.

## Consequences for the two candidate issuances

### 05:30 Europe/Berlin

- **V** No same-morning EXAA result exists yet.
- **I** A 05:30 issue can be a genuine early forecast, but its actual feature set must come from the weather and fundamentals availability audits. It must not backfill later official forecasts into historical 05:30 rows.

### 11:30 Europe/Berlin

- **V** This is only 30 minutes before the normal 12:00 SDAC gate and leaves little recovery margin.
- **V** On an EXAA trading day, matching may finish by 10:30, so a result can physically exist before 11:30. That is not evidence that an eligible public feed is complete by then.
- **V** On weekends and non-trading days, the relevant D+1 curve may have been auctioned on an earlier trading day.
- **I** A later update can still be valuable because newer weather runs and official forecasts may be available. It should be specified independently of EXAA. The exact cutoff must reserve bounded time for ingestion, completeness checks, fallback, scoring, persistence, and publication before noon.

Do not train one model with an EXAA column populated from today's database and call it point-in-time correct. **V** None of the examined public routes preserves a supported historical first-seen EXAA feed. A late-origin EXAA candidate can be evaluated only after prospective collection, or from a licensed historical source that is outside the current scope.

## Smallest task that could reopen EXAA

This task is optional and should not block an EXAA-free initial specification:

1. Ask EXAA or Wiener Börse and Fraunhofer ISE in writing whether the public JSON may be polled at zero cost for a non-commercial, public informational forecast; whether model-input use and publication of derived forecasts are permitted; what attribution is required; and whether a supported interface is available.
2. Only after permission, poll the supported route from 10:00 through 11:15 Europe/Berlin on at least 30 consecutive EXAA trading days, honoring all published rate limits.
3. Persist request time, response headers, checksum, auction day, delivery day, product, quarter-hour, result completeness, correction time, failure, and retry outcome. Cover a Friday with several delivery days, at least one non-trading day, and any delayed auction encountered.
4. Set an operational cutoff only from the observed completeness distribution and a declared safety margin. Thirty days can reject obvious infeasibility; it is not an SLA or proof of annual-tail reliability.
5. Accumulate enough prospective history before adding EXAA to the model bake-off. Until then, treat it as unavailable in both training and inference.

## Primary evidence probes

All probes below were performed on 2026-09-12:

- `https://www.exaa.at/data/trading-results` returned four current delivery days. A detailed DE unknown-origin query returned hour, block, and 96 quarter-hour products, with `AuctionDay` but no source-publication timestamp.
- The EXAA website JavaScript identifies `/data/trading-results` and `/data/market-results` as page-internal endpoints; no public API documentation, versioning, rate limit, or deprecation policy was found.
- `https://api.energy-charts.info/openapi.json` listed only bidding-zone price endpoints and contained no EXAA identifier.
- `https://www.energy-charts.info/charts/price_spot_market/data/de/week_15min_2026_37.json` contained a 672-cell EXAA series with `allowCsvDownloadForItem: false`.
- The ENTSO-E extraction guide marks A44's auction, process, business, and contract-market-agreement request fields as unused, confirming that the supported query cannot distinguish the 10:15 exchange curve.
