# Point-in-time electricity fundamentals for DE-LU

Accessed and probed: 2026-09-12. Status tags: **V** = verified in primary documentation or a direct first-party download, **O** = observed in the 2026-09-12 SMARD snapshot, **I** = inference from verified facts, and **U** = not established.

## Decision

Use SMARD as the licensed public acquisition route for DE-LU load and generation values, while preserving ENTSO-E identities and semantics in the data contract. Direct ENTSO-E is also an eligible value source for the day-ahead total-load forecast, which appears on ENTSO-E's CC BY 4.0 free-reuse list. ENTSO-E documentation and the registered-user interface can validate provenance and submission semantics, but unlisted ENTSO-E values must not enter the public product without permission. Do not treat matching SMARD and ENTSO-E rows as independent predictors. SMARD's handbook says it automatically obtains most market data from the ENTSO-E Transparency Platform, validates and transforms them, and republishes them. [SMARD user guide](https://www.smard.de/en/user-guide), [ENTSO-E free-reuse list and terms](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions)

This source decision does not make today's SMARD history point-in-time correct. SMARD updates past values when the upstream transmission system operators update ENTSO-E, closes gaps, and replaces preliminary values with quality-assured values without a fixed revision schedule. A downloaded-later value therefore proves the value for its delivery interval, but not the value known at a historical Forecast Origin.

The two candidate issue times have materially different information sets:

- At **05:30 Europe/Berlin on D-1**, no official interval-level forecast for load, wind, or solar for delivery day D is guaranteed. Only calendar, weather-run, market-history, and safely lagged actual or forecast-error features should be assumed.
- At **11:30 Europe/Berlin on D-1**, the day-ahead total-load forecast for D is due by 10:00 and is conditionally eligible after a successful, timestamped first-seen capture. The official wind and solar day-ahead forecasts for D are not due until 18:00 and are ineligible for any pre-SDAC issue.
- For **D+2 through D+10**, ENTSO-E provides no interval-level load or renewable-generation forecast contract comparable to D+1. The week-ahead load product contains one daily maximum and minimum, not a 15-minute profile. Extended forecasting must not silently forward-fill a D+1 official curve.

Actual series and fixed historical wind/solar forecasts remain useful as lagged inputs, targets for auxiliary models, and realised evaluation data. Their eligibility at each Forecast Origin must be computed from an immutable first-seen record or a conservative publication bound, never from delivery time alone.

## Source and feature availability matrix

All listed DE-LU SMARD series begin at the bidding-zone boundary on 2018-10-01. Pre-boundary DE/AT/LU rows belong to a different market regime and must keep that zone identity. `PT15M` below means native 15-minute power data at ENTSO-E; SMARD divides MW by four and publishes energy per interval in MWh.

| Feature | SMARD / ENTSO-E semantics | Resolution and earliest DE-LU date | Publication and revision behavior | Snapshot quality observations | Point-in-time use |
| --- | --- | --- | --- | --- | --- |
| Actual total load | Total load including grid losses and excluding stored energy. SMARD may contain estimated generation components and later MaBiS replacements. | Native `PT15M`; 2018-10-01. | **V** No later than H+1. Mutable. SMARD documents MaBiS replacement from at least the 42nd working day for 50Hertz and TenneT in its September 2021 guide, and says methods differ by TSO. | **O** Complete in the audited current snapshot. | Current snapshot is not a historical vintage. Prospectively eligible as a lag when a captured revision preceded the Forecast Origin. Final version is the realised evaluation reference. |
| Day-ahead total-load forecast | TSO forecast of total load for each interval of the following day. | Native `PT15M`; 2018-10-01. | **V** Due no later than two hours before day-ahead gate closure, which is 10:00 Europe/Berlin for a 12:00 closure. It must be updated after a significant change, defined as at least 10 percent in one MTU. | **O** Exactly one null delivery day, 2020-01-31, in the audited current snapshot. | Ineligible at 05:30. Conditionally eligible at 11:30 only from captured first-seen versions. A current historical snapshot is not sufficient to replay the 10:00 version. |
| Actual onshore wind | Net generation fed into the public grid, aggregated by production type. | Native `PT15M`; 2018-10-01. | **V** Initial actual or estimate no later than H+1; measured values may replace estimates. | **O** Complete in the audited current snapshot. | Prospectively eligible as a safely lagged feature. Current corrected history is not strict vintage evidence. |
| Actual offshore wind | Same net-generation definition, separate offshore category. | Native `PT15M`; 2018-10-01. | **V** H+1, mutable. | **O** No missing intervals found in the audited snapshot. | Same as actual onshore wind. |
| Actual photovoltaic | Net generation fed into the public grid. Several TSO values are estimates rather than meter-only observations. | Native `PT15M`; 2018-10-01. | **V** Initial actual or estimate by H+1, then mutable as measurements become available. | **O** Complete in the audited current snapshot. | Same as actual onshore wind. Preserve quality or estimate status when exposed. |
| Day-ahead onshore wind | TSO net-generation forecast based on measurement, weather, and geodata. | Native `PT15M`; 2018-10-01. | **V** Process type A01 is the fixed copy of the most recent current forecast at 18:00 Brussels time D-1. It is not due before SDAC. | **O** Complete in the audited current snapshot, including 100 intervals on autumn DST days. | Ineligible for forecasting its own delivery day at 05:30 or 11:30. Eligible as a fixed, lagged historical forecast or auxiliary-model label. |
| Day-ahead offshore wind | Same as day-ahead onshore, offshore category. | Native `PT15M`; 2018-10-01. | **V** Fixed at 18:00 D-1. | **O** No missing intervals found in the audited snapshot. | Same as day-ahead onshore wind. |
| Day-ahead photovoltaic | Same as day-ahead wind, solar category. | Native `PT15M`; 2018-10-01. | **V** Fixed at 18:00 D-1. | **O** Complete in the audited current snapshot, including 100 intervals on autumn DST days. | Same as day-ahead onshore wind. |
| Intraday wind and photovoltaic forecasts | Current-day renewable forecasts, updated during intraday trading. ENTSO-E also defines a fixed A40 value at 08:00 on delivery day. | Native `PT15M`; DE-LU coverage requires a source-level manifest rather than assuming the day-ahead start date. | **V** Process type A18, named `Intraday total`, carries the latest mutable current forecast. A40 is the fixed copy of the most recent forecast at 08:00 on delivery day. | **U** Exact DE-LU series starts and gaps were not established by this audit. | Never a forecast of D at a D-1 pre-SDAC origin. At 11:30, A40 can describe D-1; at 05:30, the latest eligible A40 is for D-2. A18 is backtest-unsafe without captured versions. |
| Realised residual load | SMARD-derived actual load minus actual photovoltaic, onshore wind, and offshore wind. | Derived `PT15M`; 2018-10-01. | Inherits all component availability and revisions. SMARD calculations may differ slightly because it computes before rounding. | Missing whenever any component is missing. | Derive internally from versioned components. Do not ingest the rounded SMARD derivative as independent truth. |
| Forecast residual load | SMARD-derived day-ahead load minus day-ahead photovoltaic, onshore wind, and offshore wind. | Derived `PT15M`; 2018-10-01. | The components do not share a pre-auction deadline: load is due by 10:00, while wind and solar are due at 18:00. | Missing whenever any component is missing. | The published SMARD product is ineligible for 05:30 and 11:30 D-1 because its renewable components are post-SDAC. Build an issuance-specific residual-load estimate only from features eligible at that origin. |

### Reproducible current-snapshot check

The snapshot check read the weekly JSON used by SMARD's own chart application for filters `410`, `411`, `4067`, `1225`, `4068`, `123`, `122`, and `125`, region `DE`, resolution `quarterhour`. Over the half-open UTC interval `2018-09-30T22:00Z` to `2026-09-10T22:00Z`, corresponding to complete local delivery days from 2018-10-01 through 2026-09-10, each series supplied all 278,592 distinct expected timestamps with no duplicates. The only null values were all 96 intervals of the day-ahead total-load forecast for local delivery date 2020-01-31. Actual load, actual and A01 onshore wind, offshore wind, and photovoltaic were complete in this current snapshot. All three audited autumn clock-change days had 100 UTC-distinct rows; none had the four-interval gap stated in the earlier draft.

All 3,328 weekly file requests succeeded during this one probe. That is useful evidence of current availability, but it is not an operational SLA, a completeness guarantee, or a supported bulk-API contract. SMARD can backfill or replace values later, and the chart payload's `meta_data.created` records file generation rather than first source availability. The implementation specification must require a stored completeness manifest per acquisition date, feature, source version, and UTC interval. DST days must be counted in UTC intervals and then checked as 92, 96, or 100 local Market Time Units, not as a hard-coded 96 rows.

## Publication clocks and the usable information set

Commission Regulation (EU) 543/2013 establishes the maximum publication delays:

- total load actual: no later than one hour after the operating period;
- day-ahead total-load forecast: no later than two hours before the local day-ahead gate closure, with significant updates;
- wind and solar day-ahead forecast: no later than 18:00 Brussels time D-1;
- wind and solar intraday forecast: regular updates including at least one at 08:00 on delivery day;
- aggregated generation by type and actual or estimated wind/solar generation: no later than one hour after the operating period, with measured-value updates for wind and solar.

The same Regulation requires updates to be timestamped, archived, and publicly available for at least five years. ENTSO-E documents that registered users can inspect a final value's UTC publication timestamp and `Value History`, which lists all historical submissions by the data provider. It does not document an equivalent complete-version-history contract for the ordinary REST extraction response. A later current download is therefore not a substitute for an as-of acquisition log. [Regulation 543/2013](https://eur-lex.europa.eu/eli/reg/2013/543/oj), [ENTSO-E value details and value history](https://transparencyplatform.zendesk.com/hc/en-us/articles/33729752039441-Value-details-and-value-history), [ENTSO-E data extraction implementation guide](https://www.entsoe.eu/data/transparency-platform/mop/)

For wind and solar, ENTSO-E distinguishes:

- **A01 Day-ahead**: the fixed copy of the most recent current forecast at 18:00 D-1;
- **A40 Intraday process**: the fixed copy of the most recent current forecast at 08:00 on delivery day;
- **A18 Intraday total**: the latest mutable current forecast.

Only the fixed A01 and A40 products have stable retrospective forecast semantics, but neither supplies D renewable forecasts before SDAC. A current A18 download cannot reconstruct what A18 looked like at an old Forecast Origin. [ENTSO-E Detailed Data Descriptions](https://eepublicdownloads.entsoe.eu/clean-documents/Transparency/MoP_Ref2_DDD_v3r4.pdf)

## SMARD versus direct ENTSO-E

| Concern | SMARD | Direct ENTSO-E |
| --- | --- | --- |
| Lineage | **V** Mostly an automated, checked, transformed republication of ENTSO-E. | Upstream platform receiving TSO and other data-provider submissions. |
| Units | Converts interval-average MW to MWh by dividing by four for `PT15M`. | Publishes MW for these load and generation series. |
| Geography | Convenient DE-LU, former DE/AT/LU, country, and TSO views. | Bidding-area and control-area identifiers with original document semantics. |
| Revisions | Current checked view, no fixed SMARD revision process, no per-record first-publication time. | Versioned submissions exist and the web UI can expose older versions and submission time, but ordinary extraction must be proven per product before relying on complete version history. |
| Access | Public Data download UI. The chart application exposes weekly JSON, but SMARD does not document it as a stable bulk API. | Free platform access; REST requires registration and a security token and limits query volume. |
| Public reuse | **V** SMARD states that all Market data visuals and Data download values are reusable under CC BY 4.0 with attribution. | **V** Only items on ENTSO-E's published free-reuse list can be reused without primary-owner permission. The 2023 list includes day-ahead total-load forecast but does not include actual total load, wind/solar forecasts, or actual generation. Treat direct reuse of those unlisted values as conditional on written permission. [ENTSO-E legal terms and free-reuse list](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) |

Use one canonical feature row per source document and revision. Do not independently ingest identical SMARD and ENTSO-E values and then use both as separate predictors. ENTSO-E documentation and registered-user metadata are useful for provenance, fixed process types, submission metadata, and validation. SMARD is the initial public-reuse path for the values it republishes; direct ENTSO-E day-ahead load is the only audited direct value path already cleared for reuse.

## Netztransparenz assessment

Netztransparenz provides an authenticated machine-to-machine Web API using OAuth 2.0 client credentials. Its documentation lists 15-minute wind and solar forecasts and 15-minute marketed-quantity forecasts, generally updated once daily. The historical total wind and solar forecast series ends on 2022-12-14 because the site says it then became identical to the marketed-quantity forecast. The replacement describes EEG quantities marketed by the TSOs, not total DE-LU renewable generation, and the method and distribution changed at the boundary. [Netztransparenz Web API documentation](https://www.netztransparenz.de/xspproxy/api/staticfiles/ntp-relaunch/dokumente/web-api/dokumentation-webserviceapi-netztransparenz_v1.14.pdf), [Web API FAQ](https://www.netztransparenz.de/de-de/FAQ/FAQ-WebAPI)

No authoritative clock time within the stated daily cycle, immutable vintage contract, or public redistribution permission was verified for these series. The site copyright notice requires prior written consent for reproduction of site content. Netztransparenz is therefore a research-only candidate until written reuse terms and observed first-seen timing are established. It must not be conflated with total wind or solar generation.

No additional generation category is mandatory for the first specification. If empirical testing later justifies lagged dispatchable generation, ingest the individual SMARD categories and derive an aggregate internally. They inherit H+1 publication semantics, source-specific coverage limitations, and the same revision problem as the audited actual renewable series.

## Required acquisition and selection contract

Every response or source document must preserve:

- source, endpoint, request parameters, document identifier, and upstream business/process type;
- bidding zone or control area and the exact semantic definition;
- delivery start and end in UTC, market date, local offset, resolution, unit, and quality status;
- source document version or revision identity when supplied;
- source publication or submission time when supplied;
- first successful observed availability, ingestion time, HTTP metadata, checksum, and raw payload location;
- licence and attribution version;
- parser and feature-definition versions.

Feature selection must require `available_at_utc <= information_cutoff_utc`. `available_at_utc` is the conservative maximum of a supplied publication timestamp, a documented era-specific publication bound, and the project's observed first-seen time according to a versioned policy. A revised record is a new immutable observation, not an overwrite. A separate latest-corrected view may point to the newest revision for realised evaluation.

## Acceptance gates to encode in the later specification

1. Run the SMARD completeness audit on every acquisition and retain its compact manifest. Enumerate all missing UTC intervals and separate genuine gaps from DST-local rendering defects.
2. Prospectively poll the day-ahead total-load series around 09:30-10:30 and the actual series around H+1 for at least 30 issuance days. Record first-seen and correction times before enabling those values in a production model, then choose an operational safety buffer.
3. Verify whether ENTSO-E's supported current platform export can retrieve the complete version and submission-time history for the exact DE-LU documents. If it cannot, rely on prospective immutable capture rather than scraping the UI.
4. Seek written ENTSO-E and Netztransparenz clarification only if their otherwise restricted data materially improve the empirical bake-off. Their absence does not block a SMARD-based initial specification.
5. Evaluate 11:30 day-ahead load forecast availability as an optional late-issuance feature. The model must retain a registered fallback that uses the 05:30-compatible feature set when the forecast is late or incomplete. These measurements gate individual feature admission, not completion of the architecture specification.
