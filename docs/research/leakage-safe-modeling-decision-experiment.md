# Leakage-safe modeling decision experiment

Research completed 2026-09-13 for [Design the leakage-safe modeling decision experiment](https://github.com/bhanuprasanna2001/delu/issues/9).

## Decision

Do not select a final model family from literature or from retrospective fit. Run one staged, pre-registered, rolling-origin bake-off on immutable point-in-time snapshots. The first stage contains only seasonal naive forecasts, a faithful hourly LEAR benchmark, direct quarter-hour LightGBM point and quantile models, and two explicit ways of using hourly labels. Neural, foundation-model, reconciliation, per-horizon, and ensemble candidates enter only if the simple stage leaves a measurable gap.

The native DE-LU quarter-hour regime is the only source of quarter-hour supervision and the only scored target regime. Legacy hourly observations may supervise an hourly mean, provide a cross-fitted hourly forecast feature, or contribute an aggregate loss. They must never be copied into four quarter-hour training labels. Pre-split DE/AT/LU observations are a separate optional ablation and need stronger evidence than same-zone hourly history.

The experiment makes separate decisions for:

- D+1 at the 05:30 Early Issuance;
- D+1 at the 11:30 Late Issuance with and without EXAA;
- D+2 through D+10 at each Issuance Slot;
- point forecasts; and
- the five published quantiles q10, q25, q50, q75, and q90.

A single family is not required to win every scope. A registered forecast package may contain a point component and a probabilistic component from different families. The package, its component versions, and post-processing are one reproducible candidate artifact.

## Facts that constrain the experiment

The resolved target audit establishes three non-interchangeable label regimes: DE/AT/LU hourly from 2018-01-01 through 2018-09-30, DE/LU hourly from 2018-10-01 through 2025-09-30, and native DE/LU quarter-hour from 2025-10-01. The 60-minute index after the transition is the arithmetic mean of four native quarter-hour prices. See [DE-LU SDAC target history and regime boundaries](https://github.com/bhanuprasanna2001/delu/blob/006c16254f2333d9e81e3f7981500296f8bf15bb/docs/research/sdac-target-history.md).

The resolved source and timing decisions also impose these constraints:

- every feature revision must have `source_available_at <= information_cutoff`;
- the Early cutoff is 05:30 Europe/Berlin and excludes same-morning EXAA and the official D+1 load forecast;
- the Late cutoff is 11:30 Europe/Berlin and conditionally admits a complete D+1 ENTSO-E A44 Sequence 2 EXAA curve;
- official D+1 renewable forecasts fixed at 18:00 are forbidden at both origins;
- D+2 through D+10 cannot use EXAA or official interval-level load and renewable forecasts;
- direct GEFS issued runs are the common historical weather candidate; and
- corrected present-day SMARD fundamentals are not historical point-in-time features unless a then-available revision can be proved.

These decisions are recorded in [Point-in-time fundamentals](https://github.com/bhanuprasanna2001/delu/blob/12f86ada01df56c80d4091fca875936c07739a37/docs/research/point-in-time-fundamentals.md), [Point-in-time weather forecasts through D+10](https://github.com/bhanuprasanna2001/delu/blob/d9b8a63/docs/research/weather-forecast-archives.md), [Choose the eligible source portfolio and fallbacks](https://github.com/bhanuprasanna2001/delu/issues/11), [Define the temporal and revision truth model](https://github.com/bhanuprasanna2001/delu/issues/7), and [Choose forecast origins and horizon information sets](https://github.com/bhanuprasanna2001/delu/issues/8).

Lago et al. recommend strong naive and LEAR benchmarks, ex-ante hyperparameter selection, realistic recalibration, statistical comparison, computation-time reporting, and a final time-ordered test segment for electricity-price forecasting. Their benchmark is hourly and cannot be copied mechanically onto the new DE-LU quarter-hour regime, but its experimental discipline applies directly. [Lago et al. 2021](https://doi.org/10.1016/j.apenergy.2021.116983)

## Questions the bake-off must answer

1. Does same-zone Legacy Hourly Label history improve native quarter-hour forecasts after accounting for the structural break?
2. Does the pre-split DE/AT/LU regime add incremental value beyond DE/LU hourly history?
3. Is the simplest useful bridge an hourly forecast feature, an hourly-plus-shape decomposition, or a shared multi-resolution objective?
4. Does one global horizon-aware Extended model suffice, or do horizon groups need separate models?
5. Does the 11:30 EXAA input improve D+1 forecasts on like-for-like paired origins?
6. Do raw LightGBM quantiles calibrate adequately, and does chronological conformal calibration improve coverage without excessive width or WIS loss?
7. Do any neural, foundation, reconciliation, or ensemble challengers earn their additional cost and operational surface?

Each question is answered by a paired ablation. Changing a feature set, training regime, model family, and calibration method at once is forbidden because the source of any gain would be unknowable.

## Forecasting and scoring unit

The atomic row is one Forecast Interval identified by Issuance Slot, Forecast Origin, Input Profile, product, `delivery_start_utc`, and target revision. Market Delivery Day, local start, UTC offset, Interval Position, horizon in minutes, and horizon day D+1 through D+10 are attributes.

All models receive and emit rows on the canonical half-open UTC grid. A normal local Market Delivery Day has 96 rows, a spring DST day 92, and an autumn DST day 100. No model may reshape a day to an unconditional length of 96. Complete-curve validation happens before scoring.

For legacy supervision, define an hourly mean only over the four native quarter-hours belonging to the same actual UTC hour:

`hour_mean = (q1 + q2 + q3 + q4) / 4`

This matches the post-transition 60-minute price-index definition. It does not create four labels from an old hourly observation. The two repeated local autumn hours remain different UTC hours.

Train and score signed EUR/MWh values. MAPE and log transforms are unsuitable because prices can be zero or negative. LEAR alone uses its published median/MAD standardization followed by the inverse hyperbolic sine transform, fitted on its training window and inverted after prediction. Do not clip target spikes. All scalers, encoders, spatial masks, residual distributions, and conformal corrections are fitted on training or calibration data only.

## Frozen feature families

Every family is generated independently for each historical Forecast Origin by the same as-of selector used in production.

### Common core

- admissible SDAC price curves, including the full D0 curve already cleared before either cutoff;
- price vectors or statistics at D-1, D-2, D-3, D-7, and the latest already-known same-weekday day;
- day of week, German public holiday, month or annual cyclic terms, local quarter, UTC offset, DST transition flag, horizon day, and explicit market-regime flags;
- known price-bound and Core flow-based-coupling regime indicators; and
- missingness and age fields that existed at the origin.

### Weather profile

Use only the exact eligible issued GEFS run selected for the origin. Candidate summaries include capacity-weighted onshore and offshore wind components, capacity-weighted radiation and cloud fields, population-weighted temperature, pressure, ensemble mean and spread, and source lead time. Spatial masks and capacity vintages are versioned and are fitted or selected without the test period. Interpolation to a quarter-hour grid does not turn 3-hourly or 6-hourly NWP fields into new observations.

Run a paired `core` versus `core_gefs` ablation. Recent direct ECMWF and horizon-local ICON profiles are separate, paired prospective experiments on their common coverage. They cannot replace GEFS silently or decide the value of 2018-present history.

### Late-only D+1 profile

`late_exaa` adds only a validated exact-delivery-day Sequence 2 curve and its auction age. `late_no_exaa` is otherwise identical. The official load forecast remains absent until the prospective admission gate from the source decision has passed. If later admitted, test it as one further paired ablation with an exact no-load counterpart.

## Mandatory baselines

### B0: deterministic seasonal naive

Produce two point baselines and preselect the better one on development folds only:

1. `last_curve`: map the latest cleared complete Market Delivery Day curve available at the origin to the target day's local wall-clock quarters.
2. `same_weekday`: use the most recent already-cleared curve with the target weekday. For D+h, step backward by whole weeks until the source delivery day is no later than D0. This prevents D+7 or longer horizons from accidentally referencing an uncleared future day.

For a spring target, emit only its 92 real intervals. For an autumn target, map both offset-distinct 02:00 hours; when the source day has only one 02:00 hour, use the same source wall-clock values for both target hours. This is an explicit forecast rule, not label fabrication.

### B1: empirical probabilistic naive

Around the selected deterministic naive, estimate residual q10, q25, q50, q75, and q90 from only previously observed forecast errors. Pool by Issuance Slot and horizon day. Add weekday and local-quarter conditioning only when that exact cell has at least 30 past residuals; otherwise use the broader pool. Freeze the residual quantiles at each twice-monthly refit. This is the mandatory probabilistic benchmark.

### B2: faithful hourly LEAR point baseline

LEAR is a parameter-rich ARX model with one LASSO regression per delivery hour. The published specification uses all 24 prices from D-1, D-2, D-3, and D-7, eligible delivery-day and lagged exogenous vectors, and seven weekday dummies. It selects the LASSO penalty through the training sample and applies an inverse-hyperbolic-sine variance-stabilizing transform. [Lago et al. 2021](https://doi.org/10.1016/j.apenergy.2021.116983) The official implementation confirms the feature construction, transform, and per-hour LASSO fits. [epftoolbox LEAR source at commit `47d6e06`](https://github.com/jeslago/epftoolbox/blob/47d6e0629f65ebd19d3c12cb5689dbad0c2ea078/epftoolbox/models/_lear.py)

Implement two auditable variants for D+1:

- `LEAR-P`: price vectors and weekday dummies only;
- `LEAR-X`: the same structure plus only the issued-run weather or Late-only EXAA vectors eligible for that Input Profile.

Use the published 56, 84, 1,092, and 1,456 day windows where sufficient history exists and average their forecasts as the LEAR ensemble. A window that cannot be filled is absent rather than padded. Fit only on ordinary 24-hour Market Delivery Days, because the published 24-head design does not define a 23rd or 25th local-hour head. At forecast time, omit the nonexistent spring 02 hour and apply the 02-hour head to each offset-distinct autumn 02 hour. Repeat each predicted hourly value across its four output quarter-hours. This is deliberately a coarse quarter-hour forecast baseline and is never presented as observed quarter-hour training truth.

The pinned epftoolbox implementation is AGPL-3.0. It is a scientific reference, not an automatic production dependency. A later implementation must either be licence-compatible or reproduce the published model specification independently.

All candidates, including LEAR, refit only on the production-like 3rd and 18th schedule. A separately reported daily-refit LEAR may be a diagnostic ceiling but cannot compete for selection unless every candidate receives the same retraining opportunity.

### B3: production-cadence regularized ARX

For D+2 through D+10, where classic LEAR is not a defined benchmark, fit one global LASSO ARX on Forecast Interval rows with horizon-day and local-quarter effects, admissible price lags, calendar, and the same known-future features. This supplies a transparent linear extended-horizon baseline without calling a materially different model "LEAR".

## Required simple challengers

### C1: native-quarter-hour LightGBM

Fit a row-wise, horizon-aware LightGBM on native quarter-hour labels only:

- one point model with an L1 objective;
- five separate quantile models with the LightGBM `quantile` objective and `alpha` set to 0.10, 0.25, 0.50, 0.75, and 0.90; and
- separate candidate artifacts for Early D+1, Late D+1 profiles, Early Extended, and Late Extended.

LightGBM's official parameter reference defines the quantile objective and `alpha`; the original paper documents the gradient-boosted tree implementation. [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html#objective-parameters), [Ke et al. 2017](https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html)

Use a deliberately small, predeclared hyperparameter search over leaves, minimum leaf size, learning rate, estimators, feature fraction, and L1/L2 regularization. Optimize point MAE or mean pinball loss on inner time-ordered validation origins. Do not tune on the blind period or on individual test slices.

### C2: hourly core plus learned quarter-hour shape

This is the simplest direct test of whether long hourly history helps:

1. Fit an hourly LEAR or hourly LightGBM core on the selected hourly regime set.
2. On native quarter-hour training days, define each within-hour residual as the observed quarter-hour price minus that hour's observed four-quarter mean.
3. Fit a native-only quarter-hour residual model using quarter position, calendar, weather, horizon, price lags, and a cross-fitted hourly-core forecast.
4. Project the four predicted residuals within each actual UTC hour to zero mean, then add them to the predicted hourly core.

The zero-mean projection makes the point forecast coherent with the hourly core while all within-hour shape is learned exclusively from native labels. Hourly-core predictions supplied to the residual model must be rolling out-of-fold predictions, never in-sample fitted values.

For probabilistic output, do not add residual quantiles to an hourly point and call the result calibrated. Instead, fit the five native-target LightGBM quantile models from C1 with the cross-fitted hourly-core point forecast as an additional feature. This `C2-Q` bridge lets historical hourly labels influence the conditional quarter-hour distribution while every quantile loss still uses native quarter-hour truth. Apply the same H0/H1/H2 ablation to that feature.

Run three otherwise identical history modes:

- `H0`: native period only, using its true hourly means;
- `H1`: add DE/LU Legacy Hourly Labels from 2018-10-01;
- `H2`: add the 2018 pre-split DE/AT/LU observations with a separate zone/regime indicator.

This three-way ablation is the primary decision about legacy history.

### C3: shared multi-resolution objective

Only after C2 is reproducible, fit one compact shared-trunk multi-output network as the direct multi-resolution alternative. It emits four quarter-hour point values per actual hour. Native examples receive quarter-hour loss plus an hourly-mean loss. Legacy hourly examples receive only loss on the mean of the four latent outputs; the quarter-hour residuals are masked and receive no target. Compare joint training with hourly pretraining followed by native-only fine-tuning.

This candidate tests shared representation and transfer learning without manufacturing targets. It must use the same H0, H1, and H2 regime ablations as C2. A single-output versus vector-output neural comparison is justified because those structures have behaved differently in electricity-price forecasting, but the DE-LU result must come from this bake-off. [Marcjasz, Lago, and Weron 2020](https://arxiv.org/abs/2008.08006)

## Conditional challengers and explicit exclusions

### Temporal reconciliation

Temporal hierarchies reconcile independently produced forecasts at different aggregation levels. [Athanasopoulos et al. 2017](https://doi.org/10.1016/j.ejor.2017.02.046) Test a point reconciliation of C1 quarter-hour forecasts with the C2 hourly forecast only if their development errors are complementary. Estimate any reconciliation weight on inner validation origins. Do not impose `mean(qh marginal quantiles) = hourly marginal quantile`: quantiles do not aggregate linearly without a joint distribution. Probabilistic reconciliation is outside the minimum experiment unless joint scenarios become a product requirement.

### Neural long-horizon model

Do not launch a broad architecture search. If C1-C3 leave a material extended-horizon error, add one Temporal Fusion Transformer challenger because it directly supports known-future covariates, mixed past inputs, multi-horizon output, and quantile forecasts. [Lim et al. 2021](https://doi.org/10.1016/j.ijforecast.2021.03.012) N-HiTS is not part of the minimum: its "hierarchical" interpolation is an internal multi-rate architecture, not a solution to the project's hourly-label versus quarter-hour-label supervision problem. [Challu et al. 2023](https://doi.org/10.1609/aaai.v37i6.25854)

### Foundation-model comparator

Chronos-2 is the sole optional foundation-model comparator because its primary report and official implementation support probabilistic, multivariate, and known-future-covariate forecasting. [Ansari et al. 2025](https://arxiv.org/abs/2510.15821), [official Chronos-2 implementation at commit `4dbf163`](https://github.com/amazon-science/chronos-forecasting/tree/4dbf163c2734c089cdf7da2b86fde48862ff9c6f/src/chronos/chronos2)

Run the locked checkpoint zero-shot first. Fine-tuning is allowed only if zero-shot is competitive with the best simple model and the checkpoint licence, digest, code version, complete input schema, batch construction, and possible exposure of historical German price data in pretraining are recorded. Unknown pretraining exposure is a limitation, so a foundation model cannot establish the causal value of Legacy Hourly Labels.

### Ensembles

Only after individual forecasts are frozen, test an arithmetic mean of at most the two strongest error-diverse survivors. Estimate no per-horizon stacking model on the blind period. For quantiles, average corresponding monotone quantiles and recalibrate the resulting intervals. Do not create an ensemble when its gain is indistinguishable from its best member.

### Excluded from the minimum

- ARIMA/SARIMA grid searches: LEAR and the regularized ARX already provide stronger transparent autoregressive baselines for this high-dimensional, exogenous setting.
- one model for every quarter-hour and horizon combination: this creates hundreds of sparse estimators before evidence supports the fragmentation;
- nine independently operated Extended models: the global horizon-aware model is the maintainable default;
- recurrent, convolutional, transformer, and foundation-model sweeps: one conditional neural model and one locked foundation model are enough to test whether the class merits further work;
- target clipping, random train/test splits, retrospective best-feature selection, and synthetic quarter-hour labels; and
- probabilistic hourly-to-quarter-hour reconciliation without joint samples.

## Rolling-origin protocol

### Dataset freeze

Before any fit, write a content-addressed experiment manifest containing:

- exact Data Snapshot and Source Revision identifiers and checksums;
- target-adjudication version;
- feature-definition, spatial-mask, calendar, and market-regime versions;
- source availability basis for every selected revision;
- code commit, dependency lock, random seeds, hardware or Databricks runtime identity;
- candidate matrix and hyperparameter ranges;
- development and blind date boundaries; and
- excluded or disputed origins with reasons.

The same manifest generates every candidate's examples. Candidate-specific rows may differ only when the ablation itself changes an Input Profile. Each pairwise comparison uses the intersection of valid scored origins so missing days cannot improve a model's apparent performance.

### Minimum evidence and split

Exploratory prequential scoring may start only after 56 complete native quarter-hour Market Delivery Days are available. An architecture decision is provisional until the snapshot contains at least 365 complete native-quarter-hour delivery days, at least one spring and one autumn DST day, and all four seasons. Until then, the result may justify a simple baseline deployment but not an irreversible complex architecture.

Once that minimum exists:

1. Freeze the last 90 complete forecast-origin days as a blind confirmatory segment before tuning.
2. Use the earlier native period for expanding rolling-origin development folds, with each validation block later than all data used to fit it.
3. At each simulated day, generate both 05:30 and 11:30 examples using the exact historical cutoff and Input Profile rules.
4. Refit model artifacts on the 3rd and 18th only. Between those dates, score with the latest artifact that would have completed by the origin.
5. Admit training labels only when the exact clearing-price revision was public by the simulated training cutoff. Delivery time itself is not the availability test.
6. Tune hyperparameters and select calibration windows only on inner rolling development origins. Lock them before opening the 90-day segment.
7. Score D+1 once per slot. Score D+2 through D+10 separately by horizon day and as an equal-weight horizon macro-average. Whole-product scores include only origins whose complete horizon has realised.

The two slots are never pooled as interchangeable samples. `late_exaa` versus `late_no_exaa` is evaluated only on paired Late origins where a complete exact-day EXAA curve was admissible. Missing EXAA days remain a separate operational cohort.

## Leakage and validity test suite

Any failure rejects the run before metrics are viewed.

1. **As-of invariant:** every selected Source Revision satisfies `source_available_at <= information_cutoff` under its recorded evidence basis.
2. **Slot isolation:** deleting every record first available after 05:30 leaves every Early feature and prediction unchanged.
3. **Future mutation:** modifying or adding post-cutoff revisions leaves the frozen historical example byte-identical.
4. **Label eligibility:** each training label's publication revision was available by the model-training cutoff; no current corrected snapshot proves historical availability.
5. **Run identity:** every weather value traces to one complete eligible issued run, forecast step, valid time, object checksum, and observed or allowed inferred availability.
6. **Forbidden-feature sentinels:** official renewable forecasts published at 18:00, future SDAC prices, and incomplete or wrong-day EXAA curves are deliberately injected and must be rejected.
7. **Transformation isolation:** scalers, encoders, imputers, spatial weights learned from data, hyperparameters, residual pools, and conformal corrections contain no validation or test outcomes.
8. **Cross-fitting:** hourly-core predictions used as native-quarter-hour training features come from an earlier rolling fit that excluded the target day.
9. **Conformal chronology:** calibration residuals precede the forecast origin and are disjoint from the fit sample for the associated quantile model.
10. **Regime identity:** pre-split, DE/LU hourly, and native quarter-hour rows retain different regime identifiers; no hourly row has a fabricated quarter-hour target.
11. **Grid and DST:** every curve has unique UTC starts, 15-minute durations, monotone delivery order, and exactly 92, 96, or 100 rows for its local Market Delivery Day.
12. **Horizon availability:** target-relative lags such as D-7 are resolved against the origin and rejected whenever they point to a price curve not yet cleared.
13. **Reproducibility:** rebuilding any sampled origin from its manifest produces identical feature hashes and predictions within a declared numerical tolerance.
14. **Foundation provenance:** checkpoint digest and training-data disclosure status are recorded; an unknown training corpus is never described as leakage-free.

Also run two smoke tests: permuting training labels must destroy apparent skill, and adding a random feature must not systematically improve the blind score. These do not prove correctness, but unexpected success is a reason to stop and audit.

## Metrics

### Point forecasts

Primary loss is MAE in EUR/MWh. Report it both as:

- micro MAE across Forecast Intervals; and
- macro MAE, first averaged within Market Delivery Day and horizon day, then equally across forecast origins.

The promotion statistic is macro MAE, preventing a 100-interval autumn day from receiving more decision weight than a 92-interval spring day. Also report RMSE for spike sensitivity, signed mean error for bias, median absolute error, 95th and 99th percentiles of absolute error, and MAE skill relative to the selected seasonal naive. Do not report MAPE as a selection metric.

### Quantile forecasts

Quantile regression estimates each conditional quantile by minimizing pinball loss. [Koenker and Bassett 1978](https://www.jstor.org/stable/1913643) Proper scoring rules are required so a forecaster is rewarded for an honest distribution. [Gneiting and Raftery 2007](https://doi.org/10.1198/016214506000001437)

Use these outputs:

- mean pinball loss at each quantile and averaged equally across the five quantiles;
- weighted interval score using q10/q90, q25/q75, and q50 as the primary probabilistic score;
- empirical 80% and 50% central-interval coverage;
- mean interval width, underprediction penalty, and overprediction penalty;
- empirical quantile coverage and reliability plots by nominal quantile; and
- raw and post-processed quantile-crossing rates.

WIS is a proper score for interval and quantile forecasts and approximates CRPS when multiple central intervals are supplied. [Bracher et al. 2021](https://doi.org/10.1371/journal.pcbi.1008618) Five quantiles are too sparse to claim an exact CRPS, so do not report one unless a denser frozen quantile grid or samples are produced.

Independently trained quantiles may cross. Sort them by increasing probability as a monotone rearrangement, record the pre-rearrangement crossing rate, and score the published rearranged values. Rearrangement is a documented method for enforcing monotone quantile curves. [Chernozhukov, Fernandez-Val, and Galichon 2010](https://doi.org/10.3982/ECTA7880)

### Required slices

Report point and probabilistic metrics for:

- Issuance Slot and Input Profile;
- D+1, each of D+2 through D+10, and the Extended macro-average;
- local quarter-hour and hour;
- weekday, weekend, and German public holiday;
- meteorological season and month;
- ordinary, spring DST, and autumn DST days;
- negative-price intervals;
- high positive and extreme negative prices, using q99 and q01 thresholds computed from the training snapshot only;
- market regimes including the 2022 Core coupling and price-bound changes; and
- fallback, weather-run-age, and EXAA-age cohorts.

A slice with fewer than 30 Market Delivery Days is descriptive and cannot alone select a model. DST is always reported even with one day, but only as a correctness and risk case until more transitions accrue.

## Quantile calibration experiment

Raw LightGBM quantiles are the mandatory probabilistic candidate. Add chronological conformalized quantile regression as a post-processing ablation for the 50% and 80% central intervals. For each Issuance Slot and horizon day, reserve the most recent 56 complete, already-observed origin days available at the twice-monthly refit as calibration data and exclude them from that quantile model's fit. Compare raw and conformalized output from this identical reduced-fit model so the effect of calibration is isolated; report the full-fit raw model separately. Compute the CQR nonconformity score `max(q_low - y, y - q_high)` and expand both endpoints by the corresponding empirical calibration quantile. [Romano, Patterson, and Candes 2019](https://papers.neurips.cc/paper/8613-conformalized-quantile-regression)

Standard CQR's finite-sample guarantee relies on exchangeability, which electricity-price time series and a changing market regime do not satisfy. Therefore call this rolling CQR calibration, not guaranteed coverage, and judge it by forward empirical coverage and WIS. If static rolling CQR persistently misses coverage, Adaptive Conformal Inference is one conditional challenger, evaluated from a fresh prequential start with its learning rate tuned only on development data. [Gibbs and Candes 2021](https://papers.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html)

Do not independently conformalize all five marginal quantiles. Calibrate the two central intervals, retain the q50 model, then apply one final monotone rearrangement and report any interval-nesting correction.

## Uncertainty and comparison

The comparison unit is the Forecast Origin Market Delivery Day, not an individual quarter-hour. For each primary loss, retain the paired daily loss differential. Use a moving-block bootstrap with seven consecutive origin days, 10,000 resamples, and a fixed published seed to obtain 95% confidence intervals for absolute and relative loss differences. Repeat with 14-day blocks as a sensitivity check.

For the final frozen candidate set, compute a 90% Model Confidence Set separately for point macro MAE and probabilistic macro WIS. The procedure explicitly permits multiple statistically indistinguishable best models; when it does, choose the least complex survivor. [Hansen, Lunde, and Nason 2011](https://doi.org/10.3982/ECTA5771) Multivariate Diebold-Mariano or Giacomini-White tests may be reported as electricity-price-forecasting diagnostics, but they do not replace the block-bootstrap effect size and confidence interval. [Diebold and Mariano 1995](https://doi.org/10.1080/07350015.1995.10524599), [Giacomini and White 2006](https://doi.org/10.1111/j.1468-0262.2006.00718.x)

Do not run significance tests for every slice and then select the favorable ones. The predeclared overall scopes are confirmatory; slices are guardrails and diagnostics. If several final challengers are compared with one incumbent, use the Model Confidence Set rather than uncorrected pairwise p-values.

## Compute and operational report

For every fit and full issuance, record:

- wall time and CPU time;
- worker, CPU, memory, accelerator, runtime, and library versions;
- peak resident memory and accelerator memory;
- number and total bytes of model artifacts;
- number of component models and external model weights;
- training and inference failures;
- p50 and p95 end-to-end model inference time over historical origins;
- estimated twice-monthly training compute and monthly forecast compute; and
- whether the full Early and Late curves can be generated within their reserved operational budgets.

Use one declared CPU reference environment for all classical models. A neural or foundation candidate may also report GPU results, but it must report a production-feasible CPU path or explicitly price and justify an accelerator job. Inference alone receives at most three minutes p95 of the Late run's 15-minute publication window; data readiness, validation, persistence, and retry need the remainder. A candidate that misses this gate is rejected regardless of accuracy.

## Decision and rejection gates

Apply the following gates in order. These promote a family to an implementation candidate, not directly to production champion.

### Gate 0: validity and evidence

Reject any run with a leakage-test failure, unresolved target identity, incomplete output curve, non-reproducible snapshot, post-cutoff feature, or unrecorded model/checkpoint version. Do not inspect its accuracy for selection.

If fewer than 365 complete native days or both DST transitions are available, mark all architecture findings provisional and retain the simplest valid baseline as the deployable candidate while evidence accumulates. EXAA admission additionally needs at least 60 paired complete Late origins.

### Gate 1: beat naive and linear baselines

A point family must beat the stronger of seasonal naive and the appropriate LEAR/ARX baseline on blind macro MAE. A probabilistic family must beat empirical probabilistic naive on blind macro WIS. The 95% block-bootstrap interval for its paired loss difference must exclude no improvement.

If no family clears this gate, stop. Do not progress to neural models or ensembles.

### Gate 2: decide legacy history

Within C2 and C3, compare H1 against H0 on identical native test origins. Admit DE/LU hourly history only when:

- relative macro-MAE or macro-WIS improvement is at least 1%;
- the 95% paired block-bootstrap interval excludes no improvement; and
- no required horizon or seasonal slice is more than 5% worse with supported evidence of harm.

Compare H2 against H1 with the same tests. The pre-split regime enters only if it adds a further 1% improvement and passes every guardrail. Otherwise exclude it. A gain in hourly validation without a gain on native quarter-hour targets is a rejection.

### Gate 3: decide EXAA and optional inputs

On at least 60 paired admissible Late origins, compare the same D+1 family with and without EXAA. Admit `late_exaa` only if it improves the relevant primary score by at least 1%, its confidence interval excludes no improvement, and its spike and negative-price guardrails pass. The `late_no_exaa` artifact remains mandatory even when EXAA wins.

Apply the same paired rule to any future official-load, ECMWF, or ICON feature profile. Nominal source resolution is not evidence of forecast value.

### Gate 4: calibration

Prefer raw rearranged quantiles when both central coverages are within 3 percentage points of nominal. Admit rolling CQR when it reduces the worst absolute coverage error, brings both overall coverages within 3 points where the data permit, and increases WIS by no more than 1%. If neither calibrates, reject the probabilistic candidate rather than publish misleading intervals. Test Adaptive Conformal Inference only after this failure.

### Gate 5: pay for complexity only when it wins

Classify formula baselines as complexity 0, linear and tree models as 1, decompositions or reconciliation as 2, and neural or foundation models as 3. A higher-complexity family must:

- remain in the 90% Model Confidence Set;
- improve the applicable primary score by at least 2% over the simplest surviving lower-complexity family;
- have a 95% paired confidence interval excluding no improvement;
- avoid more than 2% overall RMSE degradation, more than 5% supported degradation in any adequately sampled required slice, and more than 10% degradation in q99 absolute error; and
- meet the three-minute p95 inference gate and the later workflow ticket's training-cost budget.

Otherwise reject it and choose the simpler survivor. A GPU-only candidate cannot advance until the production workflow has an explicit accelerator budget and fallback.

Separate horizon-specific Extended models must improve the equal-horizon macro score by at least 3%, improve at least six of nine horizon days, and pass the same guardrails. Otherwise keep one horizon-aware Extended model per slot.

### Gate 6: ensemble only for incremental value

An arithmetic two-member ensemble must improve the primary score by at least 1% over its best member, remain in the Model Confidence Set, pass calibration and slice guardrails, and stay inside the inference budget. Otherwise deploy the best simple member.

### Tie rule

When evidence does not distinguish survivors, select in this order: fewer source dependencies, lower complexity class, fewer component artifacts, lower p95 inference time, then lower training compute. Never select by a test-set metric beyond the predeclared gates.

## Reproducible experiment output

One completed bake-off must publish, as versioned MLflow artifacts or equivalent immutable files:

- the experiment manifest and candidate registry;
- train, calibration, development, and blind-origin lists;
- exact feature and target snapshot manifests;
- predictions for every candidate, origin, interval, point, and quantile before and after post-processing;
- aggregate and slice metric tables;
- calibration and reliability plots;
- paired daily loss differentials, bootstrap intervals, and Model Confidence Sets;
- leakage-test results;
- compute and cost report; and
- a decision table marking each gate pass, fail, or insufficient evidence.

The final report may select different candidates for the four operational scopes and for point versus probabilistic output. It must also say which apparently promising approaches were rejected and why. No family is the winner merely because it is newer, has finer input resolution, or scored best on one retrospective aggregate.

## Minimum execution order

1. Freeze data, splits, features, thresholds, and seeds.
2. Run leakage tests and B0-B3.
3. Run C1 and raw/rearranged quantiles.
4. Run C2 with H0/H1/H2 and the EXAA ablation.
5. Run rolling CQR.
6. Stop if the simple candidates resolve the decision.
7. Otherwise run C3, then at most one reconciliation, TFT, Chronos-2, and two-member ensemble challenger as their entry conditions are met.
8. Open the blind period once, apply the gates, and write the decision record.

This order is the minimum credible path: it directly tests the unusual multi-resolution problem before spending compute on broad architecture searches.

## Primary sources

Accessed 2026-09-13.

- [Lago et al., Forecasting day-ahead electricity prices: a review, best practices and open benchmark](https://doi.org/10.1016/j.apenergy.2021.116983)
- [epftoolbox LEAR source, pinned commit](https://github.com/jeslago/epftoolbox/blob/47d6e0629f65ebd19d3c12cb5689dbad0c2ea078/epftoolbox/models/_lear.py)
- [Koenker and Bassett, Regression Quantiles](https://www.jstor.org/stable/1913643)
- [Ke et al., LightGBM](https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html)
- [LightGBM objective parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html#objective-parameters)
- [Romano, Patterson, and Candes, Conformalized Quantile Regression](https://papers.neurips.cc/paper/8613-conformalized-quantile-regression)
- [Gibbs and Candes, Adaptive Conformal Inference Under Distribution Shift](https://papers.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html)
- [Gneiting and Raftery, Strictly Proper Scoring Rules, Prediction, and Estimation](https://doi.org/10.1198/016214506000001437)
- [Bracher et al., Evaluating epidemic forecasts in an interval format](https://doi.org/10.1371/journal.pcbi.1008618)
- [Chernozhukov, Fernandez-Val, and Galichon, Quantile and Probability Curves Without Crossing](https://doi.org/10.3982/ECTA7880)
- [Athanasopoulos et al., Forecasting with temporal hierarchies](https://doi.org/10.1016/j.ejor.2017.02.046)
- [Marcjasz, Lago, and Weron, Neural networks in day-ahead electricity price forecasting](https://arxiv.org/abs/2008.08006)
- [Lim et al., Temporal Fusion Transformers](https://doi.org/10.1016/j.ijforecast.2021.03.012)
- [Challu et al., N-HiTS](https://doi.org/10.1609/aaai.v37i6.25854)
- [Ansari et al., Chronos-2](https://arxiv.org/abs/2510.15821)
- [Amazon Science Chronos implementation, pinned commit](https://github.com/amazon-science/chronos-forecasting/tree/4dbf163c2734c089cdf7da2b86fde48862ff9c6f/src/chronos/chronos2)
- [Hansen, Lunde, and Nason, The Model Confidence Set](https://doi.org/10.3982/ECTA5771)
- [Diebold and Mariano, Comparing Predictive Accuracy](https://doi.org/10.1080/07350015.1995.10524599)
- [Giacomini and White, Tests of Conditional Predictive Ability](https://doi.org/10.1111/j.1468-0262.2006.00718.x)
