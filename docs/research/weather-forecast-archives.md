# Point-in-time weather forecasts through D+10

Accessed and probed: 2026-09-12. Status tags: **V** = verified in first-party documentation or a direct catalogue/API probe, **I** = inferred from verified facts, **U** = unknown or not contractually established.

## Decision

Use a model-run-explicit portfolio. Do not use Open-Meteo `best_match`, reanalysis, or its stitched Historical Forecast API as if they were forecasts available at a historical price-forecast origin.

1. **Backfill NOAA GEFS for the empirical bake-off.** **V** NOAA's public cloud archive exposes actual 00/06/12/18 UTC GEFS runs from 2017 onward, every six hours through at least 384 hours. Direct probes found the complete 2018-10-01 control forecast at step 264 with 2 m temperature, 10 m wind, total cloud, downward shortwave radiation and mean-sea-level pressure, plus 80 m and 100 m wind components in the companion file. This is the only audited zero-cost route that spans the requested 2018-present price history, reaches every D+1 to D+10 delivery day, and preserves ensemble information. [NOAA GEFS archive description](https://www.ncei.noaa.gov/products/weather-climate-models/global-ensemble-forecast), [2018 step-264 A-field index](https://noaa-gefs-pds.s3.amazonaws.com/gefs.20181001/00/pgrb2a/gec00.t00z.pgrb2af264.idx), [2018 step-264 B-field index](https://noaa-gefs-pds.s3.amazonaws.com/gefs.20181001/00/pgrb2b/gec00.t00z.pgrb2bf264.idx)
2. **Capture direct ECMWF Open Data as a higher-skill recent-regime candidate.** **V** IFS control and ENS 00/12 UTC runs reach 360 hours; the free endpoint is 0.25 degree GRIB2 with 3-hour steps to 144 hours and 6-hour steps thereafter. AIFS Single and AIFS ENS reach 360 hours from all four cycles at 6-hour steps. These products include temperature, 100 m wind, solar radiation, cloud and pressure fields. [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data), [IFS control](https://www.ecmwf.int/en/forecasts/datasets/set-i), [AIFS Single](https://www.ecmwf.int/en/forecasts/datasets/set-ix), [AIFS ENS](https://www.ecmwf.int/en/forecasts/datasets/set-x)
3. **Treat DWD ICON as an optional short-horizon challenger.** **V** Global ICON reaches 180 hours on its long runs, ICON-EU 120 hours, and ICON-D2 48 hours. It cannot be the D+10 backbone. Its high spatial resolution, including an ICON-D2 15-minute subset, may improve D+1 renewable features, but only a leakage-safe bake-off can justify the additional source regime. [DWD ICON database reference](https://www.dwd.de/DWD/forschung/nwv/fepub/icon_database_main.pdf), [DWD live NWP catalogue](https://opendata.dwd.de/weather/nwp/)
4. **Use Open-Meteo only as a named access layer, not as the weather model or sole provenance authority.** **V** Its Single Runs API is the only relevant Open-Meteo historical product for origin-specific backtests, but the free service is non-commercial, has no uptime guarantee, omits historical availability timestamps, and has limited run depth. Its Historical Forecast and Previous Runs products have different semantics and cannot reproduce both candidate issuance slots through D+10. [Open-Meteo Single Runs](https://open-meteo.com/en/docs/single-runs-api), [terms](https://open-meteo.com/en/terms)
5. **Exclude paid ECMWF MARS from the design.** **V** Archive access for an ordinary non-member user requires a service agreement and currently has a material annual charge. A possible research waiver is not a durable production entitlement. [ECMWF archive access](https://www.ecmwf.int/en/forecasts/accessing-forecasts/order-historical-datasets)

The final weather feature set remains an empirical decision. The availability decision is that GEFS is the common historical candidate, direct ECMWF is the recent higher-resolution and ensemble candidate, and ICON is horizon-local. No weather field may enter the production contract merely because it looks useful.

## What is available at the two proposed issuance times

The times below are Europe/Berlin. A 05:30 origin is 03:30 UTC in summer and 04:30 UTC in winter; 11:30 is 09:30 UTC in summer and 10:30 UTC in winter.

| Candidate issuance | Safe complete run for all D+1 through D+10 features | Additional short-horizon run | Finding |
| --- | --- | --- | --- |
| 05:30 | GEFS 18 UTC from the preceding calendar day; ECMWF IFS 12 UTC from the preceding calendar day; ECMWF AIFS 18 UTC from the preceding day | DWD ICON 18 UTC from the preceding day | **V** The current IFS 00 UTC run has not begun dissemination by 05:30 local. The 18 UTC IFS run ends at 144 h and cannot cover D+10. AIFS 18 UTC is scheduled for 23:45 UTC and reaches 360 h. Archived GEFS 18 UTC step 264 objects sampled in 2018, 2020, 2021 and 2026 were uploaded by about 23:17-23:37 UTC; step 384 by about 23:39-00:10 UTC. |
| 11:30 | GEFS 00 UTC; ECMWF IFS 00 UTC; ECMWF AIFS 00 UTC | DWD ICON 00 UTC | **V** IFS 00 UTC dissemination through step 360 ends at 07:34 UTC, and AIFS 00 UTC is scheduled for 05:45 UTC. Both precede 11:30 local in winter and summer. Do not depend on the 06 UTC cycle: in summer the forecast origin is only 09:30 UTC, and complete long-lead products are not safely available. |

ECMWF's official schedule gives IFS 00 UTC fields through step 360 from 06:27 to 07:34 UTC and limits 06/18 UTC IFS runs to step 144. [IFS dissemination schedule](https://www.ecmwf.int/en/forecasts/datasets/set-i) AIFS Single publishes all four 360-hour runs at 05:45, 11:45, 17:45 and 23:45 UTC. [AIFS Single schedule](https://www.ecmwf.int/en/forecasts/datasets/set-ix)

The GEFS upload times are observations, not an NOAA SLA. For example, the archived [2018-10-01 18 UTC step 264 object](https://noaa-gefs-pds.s3.amazonaws.com/gefs.20181001/18/pgrb2a/gec00.t18z.pgrb2af264) has `Last-Modified: 23:23:53 UTC`, and the [2026-09-11 18 UTC step 264 object](https://noaa-gefs-pds.s3.amazonaws.com/gefs.20260911/18/atmos/pgrb2ap5/gec00.t18z.pgrb2a.0p50.f264) has `Last-Modified: 23:24:19 UTC`. **I** The specification should select the latest complete eligible run whose observed availability precedes the forecast origin by a safety buffer, rather than hard-code an assumed delay from model initialization.

At 05:30 CEST, the DWD 00 UTC long run is too close to the boundary to be a reliable dependency. **V** In a 2026-09-12 direct-catalogue probe, the global ICON 180-hour T2M object appeared about 03:29 UTC; Open-Meteo completed conversion of that run about 03:49 UTC. DWD does not guarantee Open Data availability. The prior 18 UTC run is the conservative D+1 choice. [DWD service conditions](https://www.dwd.de/EN/ourservices/opendata/opendata.html), [Open-Meteo model-update semantics](https://open-meteo.com/en/docs/model-updates)

These findings support both proposed issuance slots. They do not choose the product origins, which also depend on electricity-market data availability.

## Full-delivery-day horizon matrix

Here D+n means the complete Europe/Berlin delivery date n calendar days after the model run date. The table is conservative for DST. A product that ends inside a delivery day is marked partial.

| Product and long run | Native maximum lead and step | D+1 | D+2 | D+3 | D+4 | D+5 | D+6 | D+7 | D+8 | D+9 | D+10 |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| NOAA GEFS, all cycles | 384 h; 6-hourly historically, currently 3-hourly to 192 then 6-hourly | Full | Full | Full | Full | Full | Full | Full | Full | Full | Full |
| ECMWF IFS control or ENS, 00/12 | 360 h; 3-hourly to 144 then 6-hourly in the free subset | Full | Full | Full | Full | Full | Full | Full | Full | Full | Full |
| ECMWF IFS control or ENS, 06/18 | 144 h | Full | Full | Full | Full | Full | Partial | No | No | No | No |
| ECMWF AIFS Single or ENS, all cycles | 360 h; 6-hourly | Full | Full | Full | Full | Full | Full | Full | Full | Full | Full |
| DWD ICON / ICON-EPS, 00/12 | 180 h; hourly to 78 then 3-hourly | Full | Full | Full | Full | Full | Full | Partial | No | No | No |
| DWD ICON-EU / EPS long run | 120 h; hourly to 78 then 3-hourly | Full | Full | Full | Full | Partial | No | No | No | No | No |
| DWD ICON-D2 / EPS | 48 h; hourly | Full | No | No | No | No | No | No | No | No | No |
| Open-Meteo Previous Runs | fixed offsets only | Full | Full | Full | Full | model-dependent | model-dependent | model-dependent | No | No | No |

**V** Open-Meteo may return hourly values even when the underlying model is 3- or 6-hourly because it interpolates to an hourly API grid. That does not create new weather information. [Open-Meteo forecast documentation](https://open-meteo.com/en/docs) Likewise, interpolation to a 15-minute market grid is a feature transformation, not observed or native 15-minute weather. Accumulated radiation and precipitation must be converted using their original accumulation intervals before any time-grid allocation.

## Open-Meteo product semantics

Open-Meteo is an access and interpolation service over named models from national weather centres. Each query must pin `models`; `best_match` is not acceptable because it automatically changes model by location and availability.

| Open-Meteo product | What it actually represents | Archive depth verified on 2026-09-12 | Point-in-time verdict |
| --- | --- | --- | --- |
| Historical Weather API | ERA5/ERA5-Land reanalysis and an Open-Meteo IFS analysis-like series. The documentation says its IFS data were assembled using simulations with the latest IFS version. | Reanalysis from 1940/1950; IFS-labelled series from 2017. | **V Not an issued forecast.** Never use it to represent information available at a historical forecast origin. It may be a separate realized-weather or climate covariate. [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) |
| Historical Forecast API | A continuous series made by stitching the first few hours of successive operational model runs. It favors near-analysis accuracy, not preservation of each run's horizon. | Documentation says about 2021/2022 depending on model. Direct probes found `best_match` in 2021, GFS in 2022 and DWD ICON in 2023 for Berlin. | **V Not suitable for D+n feature replay.** It does not answer what one run predicted for the full next ten days. [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) |
| Previous Runs API | One series per fixed 24-hour offset, `_previous_day1` through `_previous_day7`. | Most models from January 2024; documented exceptions include GFS 2 m temperature from March 2021 and JMA from 2018. A probe found ECMWF IFS 0.25 offsets beginning 2024-02-04. | **V Useful for skill diagnostics, not the two issuance contracts.** It stops at seven days and does not expose the exact run cycle or historical public-availability time needed to distinguish 05:30 from 11:30. [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api) |
| Single Runs API | A run selected by UTC initialization time with its forecast horizon. | ECMWF IFS 9 km from 2024-03-14; all other models from 2026-04-02. Probes confirmed the boundary. | **Partly eligible.** It preserves run structure, but `run` is initialization, not public availability, and the response has no historical availability or model-cycle field. It must use a conservative external publication schedule and immutable response capture. [Single Runs API](https://open-meteo.com/en/docs/single-runs-api) |

There is one unresolved provenance ambiguity. **U** The Single Runs documentation calls the pre-2026 ECMWF 9 km material both archived individual runs suitable for reproducing an issued forecast and "IFS Cycle 49R1 hindcasts." A hindcast generated later is not point-in-time equivalent to an operational run. The project must obtain written clarification or cross-validate representative runs against independently archived ECMWF operational objects before admitting those 2024-2026 fields as training features.

The documented 2024 start does not mean every early run covers a complete D+10 day. **V** API probes returned 241 non-null hourly values for the 2024-03-14 through 2024-07-15 00 UTC IFS runs, then 361 values from 2024-07-16. Therefore, Open-Meteo's IFS Single Runs only demonstrated full D+10 coverage from 2024-07-16. The 18 UTC IFS run remains limited to 144 h, so the 05:30 replay must select the preceding 12 UTC run.

## Direct-provider archive depth and point-in-time quality

| Source | Earliest usable issued-run evidence | Availability timestamp | Revisions and durability | Verdict |
| --- | --- | --- | --- | --- |
| NOAA GEFS on NODD/AWS | **V** NOAA documents 2017-present. Direct probes found 2017-01-01 objects through step 384 and no 2016-12-31 prefix. | **V** Each object retains an S3 `Last-Modified` upload time. | **V** NOAA explicitly says the NODD copy is not an official archive. GEFS changed from 20 perturbed members plus control to 30 plus control with v12 on 2020-09-23, and grids/layouts changed. [NCEP GEFS system history](https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gefs.php) | Best zero-cost 2018-present candidate, subject to a complete manifest and gap audit. Preserve checksums and source object metadata. |
| ECMWF Open Data portal and cloud mirrors | **V** The portal retains only 12 runs, about 2-3 days. The AWS mirror was directly observed from 2023-01-18. | **V** Dated cloud objects retain `Last-Modified`. | **U** Long cloud retention is visible but not promised. Paths, compression, streams and fields change by IFS cycle. An old 2023 long-lead subset lacked some current 100 m wind, solar and cloud fields. | Eligible from the first date each exact field exists. Start own immutable capture now. [AWS registry](https://registry.opendata.aws/ecmwf-forecasts/) |
| DWD Open Data NWP tree | **V** Current runs only; an older run returned 404 in the probe. DWD's internal system retains some native runs for about 15 months, but no supported external route was established. | **V** HTTP object modification time can be captured prospectively. | **V** DWD provides no availability guarantee. Product start dates and grids changed: global ICON in 2015, global/EU EPS in 2018, ICON-D2 in 2021, and ensemble grids changed in 2022. | Prospectively eligible after own capture. No zero-cost 2018 backfill was found. |
| Open-Meteo run archive | See product table above. | **V** Current metadata exposes latest initialization, conversion and API-availability times, but historical Single Runs responses do not. | **V** Free service has no uptime guarantee. Historical model output can span multiple upstream model cycles, and the API response does not identify that cycle. | Convenience layer and cross-check, not sole evidence of historical availability or upstream version. |

NOAA documents that GEFS NODD data from 2017 onward are publicly accessible but not officially archived. [NOAA GEFS](https://www.ncei.noaa.gov/products/weather-climate-models/global-ensemble-forecast) A full archive audit must therefore enumerate the exact control/member, step and parameter objects for every selected run instead of assuming daily completeness.

## Variables and ensembles

The zero-cost candidates expose the electricity-sensitive inputs requested by the project, but not with one homogeneous schema.

| Need | GEFS | ECMWF IFS/AIFS | DWD ICON | Open-Meteo transformation concern |
| --- | --- | --- | --- | --- |
| Wind generation | 10 m plus 80/100 m U/V components in the probed 2018 files | 10 m and 100 m U/V in current open catalogues | 10 m and model-level wind; product-specific hub-height fields | Prefer U/V components and derive speed/direction after spatial aggregation. Do not mix heights silently. |
| Solar generation | Downward shortwave radiation and cloud fields in the probed 2018 control | Surface downward shortwave radiation and low/mid/high/total cloud | Direct/diffuse shortwave and cloud fields by product | Radiation is an interval average or accumulation in several raw products. Preserve interval semantics before interpolation. |
| Load/weather demand | 2 m temperature, humidity/dew point, pressure, precipitation | 2 m temperature/dew point, pressure, precipitation | 2 m temperature/humidity, pressure, precipitation | Derived humidity or apparent temperature must name its formula/version. |
| Weather uncertainty | 20 perturbed plus control historically; 30 perturbed plus control after GEFS v12 | Current IFS ENS and AIFS ENS have control plus 50 perturbed members | ICON/ICON-EU EPS have 40 members; ICON-D2 EPS 20 | The Open-Meteo live Ensemble API is documented, but an equally deep run-level member archive is not. Do not train on live ensemble summaries without matching historical definitions. |

For probabilistic price forecasting, ensemble mean, spread and selected distribution summaries are candidate features. They are not automatically calibrated electricity-price quantiles. Their incremental value must be tested against deterministic weather and price-only baselines.

## Licensing, public output, and operational reliability

| Source | Zero-cost and public-derived-output status | Reliability consequence |
| --- | --- | --- |
| NOAA/NODD | **V** NOAA data disseminated through NODD are open for public use. NOAA requests attribution for unaltered data and prohibits implying endorsement. [NOAA GEFS AWS registry](https://registry.opendata.aws/noaa-gefs/) | Historical cloud retention is not an official archive. Use redundant live access and own raw retention. |
| DWD Open Data | **V** CC BY 4.0 permits reuse, modification and redistribution with attribution, including commercial use, subject to any third-party rights. | DWD disclaims a guaranteed public service. [DWD legal notice](https://www.dwd.de/EN/service/legal_notice/legal_notice_node.html) |
| ECMWF Open Data | **V** CC BY 4.0 permits commercial reuse and redistribution with attribution. The freely hosted subset is 0.25 degree; high-volume or customised delivery may incur service charges even though the data licence is open. | The portal is rolling and connection-limited; use at least one public cloud mirror plus own storage. [ECMWF licence](https://apps.ecmwf.int/datasets/licences/general/) |
| Open-Meteo hosted API | **V** API data are CC BY 4.0 and may be displayed or redistributed with attribution, but the hosted free service is only for non-commercial use, below 10,000 calls/day, and has no uptime guarantee. | The planned informational site is eligible only while the operator's use remains non-commercial under the published definition. Ads, paid access, data sales or other monetisation require a commercial plan or self-hosting. [Open-Meteo terms](https://open-meteo.com/en/terms), [pricing](https://open-meteo.com/en/pricing) |
| Open-Meteo self-hosted software/database | **V** The software is AGPLv3 and the weather data are CC BY 4.0. Documentation permits commercial self-hosting, with AGPL network-source obligations for modifications. | There is no provider SLA; storage, compute and operations remain the project's responsibility. [self-hosting guide](https://github.com/open-meteo/open-meteo/blob/main/docs/getting-started.md) |

This is a technical reading of published terms, not legal advice. The forecast website must show source attribution and a data/method provenance page. Keep the licence text and attribution requirements versioned with every acquisition contract.

## Required point-in-time contract

For every raw weather object or API response, store at least:

- provider and access layer
- product, upstream model, grid and model/experiment version when known
- run origin UTC
- forecast step and valid time UTC
- parameter, level, member, unit and accumulation interval
- upstream object identifier and request URL
- upstream `Last-Modified` or provider availability time when exposed
- first successful observed availability UTC
- ingestion UTC and checksum
- source licence/version
- completeness-manifest version

Training selection must require `available_at_utc <= forecast_origin_utc - safety_buffer` and choose the latest complete run under a versioned issuance-specific policy. Run origin is never a substitute for publication time. If historical availability cannot be proven from object metadata or a schedule effective in that model era, exclude the run or apply a documented conservative bound.

The spatial transformation must also be versioned. Point forecasts for Berlin are not representative of German wind and solar production. Candidate features should aggregate grid cells over documented onshore-wind, offshore-wind, solar-capacity and population/load-weighted masks. Weather-model grid changes remain explicit regimes.

## Gates before the implementation specification

1. **Inventory GEFS completeness.** Enumerate the selected 18 UTC and 00 UTC runs from 2018 onward and the exact required control/member, step and variable objects. Report gaps, layout changes, bytes and historical S3 modification times. The NODD bucket's non-archive status makes this mandatory.
2. **Clarify Open-Meteo's 2024 IFS provenance.** Obtain written confirmation that the data labelled "hindcasts" are the original operational forecasts, or reject them for point-in-time training. Independently compare sample values and horizons with ECMWF operational archive objects.
3. **Start immutable prospective capture now.** Capture GEFS, ECMWF IFS control/ENS, AIFS Single/ENS, and only the minimal ICON products needed for a future short-horizon bake-off. Raw capture, not a third-party rolling API, is the durable source of future truth.
4. **Measure observed publication latency for at least 30 issuance days.** Record first-object and complete-manifest times from every endpoint. Use the evidence to set safety buffers and fallback rules; do not infer an SLA from one probe.
5. **Bake off weather regimes.** Compare price-only, GEFS-only, GEFS plus ECMWF, and optional ICON short-horizon features under the same walk-forward origins. The weather provider decision is won by out-of-sample price performance and operational completeness, not nominal weather resolution.
