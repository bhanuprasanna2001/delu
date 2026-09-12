# DE-LU SDAC Forecasting

This context describes public forecasts of DE-LU Single Day-Ahead Coupling prices and the temporal evidence used to produce and evaluate them.

## Market

**Bidding Zone**:
A geographic market area with one SDAC clearing price for each Market Time Unit. DE-LU is the current target zone; DE-AT-LU is a distinct Legacy Market Regime.
_Avoid_: Market, region

**Market Delivery Day**:
The Europe/Berlin calendar day on which electricity is delivered. It contains 92, 96, or 100 quarter-hour Delivery Intervals depending on daylight-saving transitions.
_Avoid_: UTC day, 24-hour day

**Market Time Unit**:
The smallest delivery duration cleared natively by SDAC for the applicable market regime. It is 15 minutes for DE-LU delivery from 2025-10-01 onward.
_Avoid_: Sampling rate, display resolution

**Delivery Interval**:
An unambiguous half-open physical interval identified by Bidding Zone, applicable regime, UTC start, and duration. It is described additionally by its Europe/Berlin local time, UTC offset, Market Delivery Day, and position within that day.
_Avoid_: Naive local timestamp, quarter-hour label

**Interval Position**:
The one-based position of a Delivery Interval after ordering a Market Delivery Day by UTC start. A 15-minute day therefore has positions 1 through 92, 96, or 100.
_Avoid_: Row number, local-hour index

**Legacy Market Regime**:
The DE-AT-LU bidding-zone regime that ended after Market Delivery Day 2018-09-30. Its prices are not observations of the DE-LU target.
_Avoid_: Old DE-LU data

**Legacy Hourly Label**:
An observed hourly SDAC clearing price from before native 15-minute SDAC operation; a Market Delivery Day contains 23, 24, or 25 such labels. Four repeated copies are representations of one hourly label, not four observed quarter-hour labels.
_Avoid_: Quarter-hour price, native 15-minute price

**Native Quarter-Hour Label**:
An SDAC clearing price observed for one 15-minute Market Time Unit from Market Delivery Day 2025-10-01 onward.
_Avoid_: Upsampled hourly price

## Forecasting

**Forecast Origin**:
The scheduled real-world instant at which a forecast's permissible information set is evaluated.
_Avoid_: Run date, delivery date

**Issuance Slot**:
A recurring Europe/Berlin schedule that fixes a Forecast Origin, Information Cutoff, and publication deadline for one family of Issuances.
_Avoid_: Pipeline time, approximate morning run

**Information Cutoff**:
The latest Source Availability Time allowed into one forecast issuance. Data first available after it is forbidden even if present in the database later.
_Avoid_: Ingestion time, event time

**Source Availability Time**:
The earliest evidenced instant at which a source record or forecast run was obtainable from the supported upstream interface.
_Avoid_: Delivery time, assumed publication time

**Upstream Run Time**:
The source model's declared initialization or reference instant. It identifies a run but does not prove when its outputs became available.
_Avoid_: Source Availability Time, ingestion time

**Source Issue Time**:
The source-declared instant at which an upstream record or forecast was created.
_Avoid_: Forecast Origin, Issued At

**Source Publication Time**:
The source-declared instant at which an upstream record or forecast was released publicly.
_Avoid_: Published At, ingestion time

**First-Seen Time**:
The earliest instant at which this system successfully observed an upstream record or forecast through the supported interface.
_Avoid_: Source Publication Time, ingestion time

**Ingestion Time**:
The instant at which an obtained Source Revision was stored durably by this system. It is audit metadata, not a substitute for Source Availability Time.
_Avoid_: Source Availability Time, event time

**Source Revision Time**:
The source-declared instant at which an upstream correction or replacement was created.
_Avoid_: Ingestion Time, current value

**Issuance**:
An immutable, complete forecast curve created for one product and Forecast Origin, with its own identity. A correction or later update is a new, linked Issuance and may share the Forecast Origin, but never overwrites an earlier one.
_Avoid_: Mutable current forecast, run

**Generated At**:
The instant at which computation of a complete forecast curve finished.
_Avoid_: Forecast Origin, Issued At

**Issued At**:
The instant at which a complete forecast curve was accepted as an immutable Issuance.
_Avoid_: Source Issue Time, Published At

**Published At**:
The instant at which an Issuance first became available through the public read path.
_Avoid_: Source Publication Time, Issued At

**Source Revision**:
An immutable version of one upstream record, distinguished by source revision metadata and a payload checksum. A correction creates another Source Revision rather than replacing an earlier one.
_Avoid_: Current value, overwritten row

**Availability Evidence**:
The basis for assigning Source Availability Time: observed first-seen, an authoritative source timestamp, or a conservative fixed-schedule inference. Mutable snapshots and records whose historical availability cannot be bounded have no admissible Availability Evidence for point-in-time use.
_Avoid_: Assumed publication time

**As-Of Selection**:
The deterministic selection of the newest admissible Source Revision whose Source Availability Time is no later than an Information Cutoff.
_Avoid_: Latest value, current snapshot

**Data Snapshot**:
An immutable selection of the exact Source Revisions used to derive forecast features or labels.
_Avoid_: Current data, latest table

**Training Example**:
A target Forecast Interval paired with features eligible at one historical Forecast Origin under a Data Snapshot.
_Avoid_: Training row, randomly split row

**Input Profile**:
A named contract for the feature families admissible at an Issuance Slot. Missing inputs select another eligible Input Profile rather than being silently substituted or filled.
_Avoid_: Whatever data is available, ad hoc fallback

**Forecast Horizon**:
The elapsed time from Forecast Origin to a Forecast Interval's delivery start, additionally grouped by its Market Delivery Day offset such as D+1 or D+10.
_Avoid_: Row number, model step

**Day-Ahead Forecast**:
A forecast for every Forecast Interval in the next Market Delivery Day, issued before the normal SDAC gate closes.
_Avoid_: Realised day-ahead price

**Extended Forecast**:
A rolling forecast covering every complete Market Delivery Day from D+1 through D+10 inclusive.
_Avoid_: Ten-day point, partial tenth day

**Forecast Interval**:
A 15-minute Delivery Interval carrying a point prediction and the product's probabilistic outputs.
_Avoid_: Row number, resampled hour

**Realised Price**:
The observed DE-LU SDAC clearing price used to evaluate issued forecasts after it becomes available.
_Avoid_: Forecast, EXAA signal
