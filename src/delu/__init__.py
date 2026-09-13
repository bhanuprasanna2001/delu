from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")
FORECAST_KEYS = ("point", "q10", "q25", "q50", "q75", "q90")
SHA256 = re.compile(r"[0-9a-f]{64}")


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be an object")
    return value


def _string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _instant(value: object, name: str, *, utc_only: bool = False) -> datetime:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a timezone-aware instant")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a timezone-aware instant") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        qualifier = "timezone-aware UTC" if utc_only else "timezone-aware"
        raise ValueError(f"{name} must be {qualifier}")
    if utc_only and parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{name} must be timezone-aware UTC")
    return parsed.astimezone(UTC)


def _utc_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _offset_text(value: datetime) -> str:
    offset = value.utcoffset()
    assert offset is not None
    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    hours, remainder = divmod(abs(minutes), 60)
    return f"{sign}{hours:02d}:{remainder:02d}"


def _expected_starts(delivery_day: date) -> list[datetime]:
    start = datetime.combine(delivery_day, time.min, BERLIN).astimezone(UTC)
    end = datetime.combine(delivery_day + timedelta(days=1), time.min, BERLIN).astimezone(UTC)
    count = int((end - start) / timedelta(minutes=15))
    return [start + timedelta(minutes=15 * position) for position in range(count)]


def _validate_timing(data: dict[str, Any], delivery_day: date) -> dict[str, str]:
    names = ("information_cutoff", "forecast_origin", "generated_at", "issued_at", "published_at")
    instants = {name: _instant(data.get(name), name) for name in names}
    if list(instants.values()) != sorted(instants.values()):
        raise ValueError(
            "timing must satisfy information_cutoff <= forecast_origin <= generated_at <= issued_at <= published_at"
        )

    local_origin = instants["forecast_origin"].astimezone(BERLIN)
    if (
        local_origin.date() != delivery_day - timedelta(days=1)
        or local_origin.time().replace(tzinfo=None) != time(5, 30)
        or instants["information_cutoff"] != instants["forecast_origin"]
    ):
        raise ValueError(
            "Early Day-Ahead forecast_origin and information_cutoff must be 05:30 Europe/Berlin on D-1"
        )
    deadline = local_origin.replace(hour=6, minute=0)
    if instants["published_at"] > deadline.astimezone(UTC):
        raise ValueError("Early Day-Ahead published_at must be no later than 06:00 Europe/Berlin")
    return {name: _utc_text(value) for name, value in instants.items()}


def _validate_models(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("champion_model_versions must be a non-empty array")
    models = []
    roles = set()
    for index, raw_model in enumerate(value):
        model = _mapping(raw_model, f"champion_model_versions[{index}]")
        validated = {
            key: _string(model, key)
            for key in ("operational_model_role", "model_name", "registered_model_version")
        }
        if validated["operational_model_role"] in roles:
            raise ValueError(
                "champion_model_versions must have unique operational_model_role values"
            )
        roles.add(validated["operational_model_role"])
        models.append(validated)
    return models


def _validate_snapshot(value: object) -> dict[str, str]:
    snapshot = _mapping(value, "data_snapshot")
    snapshot_id = _string(snapshot, "data_snapshot_id")
    checksum = _string(snapshot, "manifest_sha256")
    if SHA256.fullmatch(checksum) is None:
        raise ValueError("manifest_sha256 must be a lowercase SHA-256 digest")
    return {"data_snapshot_id": snapshot_id, "manifest_sha256": checksum}


def _validate_attributions(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("source_attributions must be a non-empty array")
    fields = ("source_id", "name", "url", "licence", "licence_url")
    attributions = []
    for index, raw_attribution in enumerate(value):
        attribution = _mapping(raw_attribution, f"source_attributions[{index}]")
        validated = {key: _string(attribution, key) for key in fields}
        if not validated["url"].startswith(("https://", "http://")) or not validated[
            "licence_url"
        ].startswith(("https://", "http://")):
            raise ValueError("source attribution URLs must use HTTP or HTTPS")
        attributions.append(validated)
    return attributions


def _validate_intervals(value: object, delivery_day: date) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise TypeError("forecasts must be an array")
    expected_starts = _expected_starts(delivery_day)
    if len(value) != len(expected_starts):
        raise ValueError(f"expected {len(expected_starts)} forecasts, got {len(value)}")

    intervals: list[dict[str, object]] = []
    for index, (raw_forecast, expected_start) in enumerate(
        zip(value, expected_starts, strict=True)
    ):
        forecast = _mapping(raw_forecast, f"forecasts[{index}]")
        actual_start = _instant(
            forecast.get("delivery_start_utc"),
            f"forecasts[{index}].delivery_start_utc",
            utc_only=True,
        )
        if actual_start != expected_start:
            raise ValueError(
                f"forecasts[{index}].delivery_start_utc must be {_utc_text(expected_start)}"
            )

        values: dict[str, int | float] = {}
        for key in FORECAST_KEYS:
            if key not in forecast:
                raise ValueError(f"forecasts[{index}] is missing {key}")
            number = forecast[key]
            if (
                isinstance(number, bool)
                or not isinstance(number, (int, float))
                or not math.isfinite(number)
            ):
                raise ValueError(f"forecasts[{index}].{key} must be finite")
            values[key] = number
        quantiles = [values[key] for key in FORECAST_KEYS[1:]]
        if quantiles != sorted(quantiles):
            raise ValueError(f"forecasts[{index}] quantiles must be nondecreasing")

        local_start = actual_start.astimezone(BERLIN)
        intervals.append(
            {
                "delivery_start_utc": _utc_text(actual_start),
                "delivery_end_utc": _utc_text(actual_start + timedelta(minutes=15)),
                "delivery_start_local": local_start.isoformat(timespec="seconds"),
                "utc_offset": _offset_text(local_start),
                "market_delivery_day": delivery_day.isoformat(),
                "interval_position": index + 1,
                **values,
            }
        )
    return intervals


def build_day_ahead_artifact(value: object) -> dict[str, object]:
    data = _mapping(value, "input")
    try:
        delivery_day = date.fromisoformat(_string(data, "market_delivery_day"))
    except ValueError as error:
        raise ValueError("market_delivery_day must be an ISO calendar date") from error

    artifact: dict[str, object] = {
        "contract_version": "v1",
        "issuance_id": _string(data, "issuance_id"),
        "product": "day_ahead",
        "issuance_slot": "early",
        "status": "normal",
        "supersedes_issuance_id": None,
        **_validate_timing(data, delivery_day),
        "bidding_zone": "DE-LU",
        "covered_market_delivery_days": [delivery_day.isoformat()],
        "currency": "EUR",
        "unit": "EUR/MWh",
        "resolution": "PT15M",
        "input_profile": _string(data, "input_profile"),
        "degraded": False,
        "fallback_reason": None,
        "exaa_sequence_2_admitted": False,
        "champion_model_versions": _validate_models(
            data.get("champion_model_versions")
        ),
        "code_version": _string(data, "code_version"),
        "feature_definition_version": _string(data, "feature_definition_version"),
        "data_snapshot": _validate_snapshot(data.get("data_snapshot")),
        "canonical_day_ahead_issuance_id": None,
        "source_attributions": _validate_attributions(data.get("source_attributions")),
        "intervals": _validate_intervals(data.get("forecasts"), delivery_day),
    }
    canonical = json.dumps(
        artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {"content_sha256": hashlib.sha256(canonical.encode()).hexdigest(), **artifact}


def main() -> None:
    parser = argparse.ArgumentParser(prog="delu")
    commands = parser.add_subparsers(dest="command", required=True)
    emit = commands.add_parser(
        "emit-day-ahead", help="validate a local forecast input and emit a v1 artifact"
    )
    emit.add_argument("input", type=Path)
    emit.add_argument("output", type=Path)
    args = parser.parse_args()

    try:
        raw_input = json.loads(args.input.read_text(encoding="utf-8"))
        artifact = build_day_ahead_artifact(raw_input)
        args.output.write_text(
            json.dumps(artifact, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        parser.error(str(error))


__all__ = ["build_day_ahead_artifact", "main"]
