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
An unambiguous half-open physical interval identified in UTC and described additionally by its Europe/Berlin local time, UTC offset, Market Delivery Day, and position within that day.
_Avoid_: Naive local timestamp, quarter-hour label

**Legacy Market Regime**:
The DE-AT-LU bidding-zone regime that ended after Market Delivery Day 2018-09-30. Its prices are not observations of the DE-LU target.
_Avoid_: Old DE-LU data

**Legacy Hourly Label**:
An observed hourly SDAC clearing price from before native 15-minute SDAC operation. Four repeated copies are representations of one hourly label, not four observed quarter-hour labels.
_Avoid_: Quarter-hour price, native 15-minute price

**Native Quarter-Hour Label**:
An SDAC clearing price observed for one 15-minute Market Time Unit from Market Delivery Day 2025-10-01 onward.
_Avoid_: Upsampled hourly price

## Forecasting

**Forecast Origin**:
The scheduled real-world instant at which a forecast's permissible information set is evaluated.
_Avoid_: Run date, delivery date

**Information Cutoff**:
The latest Source Availability Time allowed into one forecast issuance. Data first available after it is forbidden even if present in the database later.
_Avoid_: Ingestion time, event time

**Source Availability Time**:
The earliest evidenced instant at which a source record or forecast run was obtainable from the supported upstream interface.
_Avoid_: Delivery time, assumed publication time

**Issuance**:
An immutable, complete forecast curve created for one product and Forecast Origin. A later update is a new Issuance and does not overwrite the earlier one.
_Avoid_: Mutable current forecast, run

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
