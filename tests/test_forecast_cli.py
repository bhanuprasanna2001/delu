from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parents[1]
BERLIN = ZoneInfo("Europe/Berlin")
FORECAST_KEYS = ("point", "q10", "q25", "q50", "q75", "q90")


def fixture_for(market_delivery_day: date) -> dict[str, Any]:
    local_midnight = datetime.combine(market_delivery_day, datetime.min.time(), BERLIN)
    next_midnight = datetime.combine(
        market_delivery_day + timedelta(days=1), datetime.min.time(), BERLIN
    )
    starts = []
    current = local_midnight.astimezone(UTC)
    while current < next_midnight.astimezone(UTC):
        starts.append(current.isoformat().replace("+00:00", "Z"))
        current += timedelta(minutes=15)

    origin = (
        datetime.combine(
            market_delivery_day - timedelta(days=1), datetime.min.time(), BERLIN
        )
        .replace(hour=5, minute=30)
        .astimezone(UTC)
    )
    as_utc = lambda value: value.isoformat().replace("+00:00", "Z")
    return {
        "issuance_id": f"early-{market_delivery_day.isoformat()}",
        "market_delivery_day": market_delivery_day.isoformat(),
        "forecast_origin": as_utc(origin),
        "information_cutoff": as_utc(origin),
        "generated_at": as_utc(origin + timedelta(minutes=1)),
        "issued_at": as_utc(origin + timedelta(minutes=2)),
        "published_at": as_utc(origin + timedelta(minutes=3)),
        "input_profile": "early_core",
        "champion_model_versions": [
            {
                "output": "point",
                "model_name": "seasonal_naive",
                "registered_model_version": "1",
            },
            {
                "output": "probabilistic",
                "model_name": "historical_residual_quantiles",
                "registered_model_version": "1",
            },
        ],
        "code_version": "9f2490f",
        "feature_definition_version": "calendar-v1",
        "data_snapshot": {
            "data_snapshot_id": f"snapshot-{market_delivery_day.isoformat()}",
            "manifest_sha256": "a" * 64,
        },
        "source_attributions": [
            {
                "source_id": "smard",
                "name": "SMARD",
                "url": "https://www.smard.de/",
                "licence": "CC BY 4.0",
                "licence_url": "https://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "forecast_intervals": [
            {
                "delivery_start_utc": start,
                "point": 50.0,
                "q10": 30.0,
                "q25": 40.0,
                "q50": 50.0,
                "q75": 60.0,
                "q90": 70.0,
            }
            for start in starts
        ],
    }


class ForecastCliTest(unittest.TestCase):
    def run_cli(
        self, fixture: dict[str, Any]
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory, "input.json")
            output_path = Path(directory, "artifact.json")
            input_path.write_text(json.dumps(fixture), encoding="utf-8")
            env = os.environ | {"PYTHONPATH": str(ROOT / "src")}
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "delu",
                    "emit-day-ahead",
                    str(input_path),
                    str(output_path),
                ],
                check=False,
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            artifact = (
                json.loads(output_path.read_text(encoding="utf-8"))
                if output_path.exists()
                else None
            )
        return result, artifact

    def test_emits_complete_ordinary_day_artifact(self) -> None:
        result, artifact = self.run_cli(fixture_for(date(2026, 1, 15)))

        self.assertEqual(result.returncode, 0, result.stderr)
        assert artifact is not None
        self.assertEqual(artifact["contract_version"], "v1")
        self.assertEqual(artifact["product"], "day_ahead")
        self.assertEqual(artifact["issuance_slot"], "early")
        self.assertEqual(artifact["status"], "normal")
        self.assertEqual(artifact["bidding_zone"], "DE-LU")
        self.assertEqual(artifact["market_regime"], "DE-LU_NATIVE_QUARTER_HOUR")
        self.assertEqual(artifact["currency"], "EUR")
        self.assertEqual(artifact["unit"], "EUR/MWh")
        self.assertEqual(artifact["resolution"], "PT15M")
        self.assertEqual(artifact["covered_market_delivery_days"], ["2026-01-15"])
        self.assertEqual(len(artifact["intervals"]), 96)
        self.assertEqual(
            [model["output"] for model in artifact["champion_model_versions"]],
            ["point", "probabilistic"],
        )
        self.assertTrue(
            all(
                model["product"] == "day_ahead"
                and model["issuance_slot"] == "early"
                and model["input_profile"] == "early_core"
                and model["horizon_responsibility"] == "D+1"
                for model in artifact["champion_model_versions"]
            )
        )

        first = artifact["intervals"][0]
        last = artifact["intervals"][-1]
        self.assertEqual(first["delivery_start_utc"], "2026-01-14T23:00:00Z")
        self.assertEqual(first["delivery_end_utc"], "2026-01-14T23:15:00Z")
        self.assertEqual(first["delivery_start_local"], "2026-01-15T00:00:00+01:00")
        self.assertEqual(first["utc_offset"], "+01:00")
        self.assertEqual(first["market_delivery_day"], "2026-01-15")
        self.assertEqual(first["interval_position"], 1)
        self.assertEqual(last["interval_position"], 96)
        self.assertEqual(last["delivery_end_utc"], "2026-01-15T23:00:00Z")
        self.assertEqual(
            [first[key] for key in FORECAST_KEYS], [50.0, 30.0, 40.0, 50.0, 60.0, 70.0]
        )

        checksum = artifact.pop("content_sha256")
        canonical = json.dumps(
            artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        self.assertEqual(checksum, hashlib.sha256(canonical.encode()).hexdigest())

    def test_emits_dst_safe_transition_days(self) -> None:
        cases = ((date(2026, 3, 29), 92), (date(2026, 10, 25), 100))

        for market_delivery_day, count in cases:
            with self.subTest(market_delivery_day=market_delivery_day):
                result, artifact = self.run_cli(fixture_for(market_delivery_day))
                self.assertEqual(result.returncode, 0, result.stderr)
                assert artifact is not None
                self.assertEqual(len(artifact["intervals"]), count)
                self.assertEqual(
                    [
                        interval["interval_position"]
                        for interval in artifact["intervals"]
                    ],
                    list(range(1, count + 1)),
                )

        spring = self.run_cli(fixture_for(date(2026, 3, 29)))[1]
        assert spring is not None
        self.assertFalse(
            any(
                "T02:" in interval["delivery_start_local"]
                for interval in spring["intervals"]
            )
        )

        autumn = self.run_cli(fixture_for(date(2026, 10, 25)))[1]
        assert autumn is not None
        repeated = [
            interval
            for interval in autumn["intervals"]
            if interval["delivery_start_local"].startswith("2026-10-25T02:00:00")
        ]
        self.assertEqual(
            [interval["utc_offset"] for interval in repeated], ["+02:00", "+01:00"]
        )
        self.assertNotEqual(
            repeated[0]["delivery_start_utc"], repeated[1]["delivery_start_utc"]
        )

    def test_rejects_invalid_curves(self) -> None:
        invalid = {}

        cardinality = fixture_for(date(2026, 1, 15))
        cardinality["forecast_intervals"].pop()
        invalid["cardinality"] = (cardinality, "expected 96 Forecast Intervals")

        non_finite = fixture_for(date(2026, 1, 15))
        non_finite["forecast_intervals"][0]["point"] = float("inf")
        invalid["non-finite"] = (non_finite, "point must be finite")

        crossing = fixture_for(date(2026, 1, 15))
        crossing["forecast_intervals"][0]["q10"] = 45.0
        invalid["quantile crossing"] = (crossing, "quantiles must be nondecreasing")

        incomplete = fixture_for(date(2026, 1, 15))
        del incomplete["forecast_intervals"][0]["q90"]
        invalid["incomplete"] = (incomplete, "missing q90")

        incomplete_models = fixture_for(date(2026, 1, 15))
        incomplete_models["champion_model_versions"].pop()
        invalid["incomplete model roles"] = (
            incomplete_models,
            "model outputs must be point and probabilistic",
        )

        for name, (fixture, message) in invalid.items():
            with self.subTest(name=name):
                result, artifact = self.run_cli(fixture)
                self.assertEqual(result.returncode, 2)
                self.assertIsNone(artifact)
                self.assertIn(message, result.stderr)

    def test_rejects_naive_local_time_as_interval_identity(self) -> None:
        fixture = fixture_for(date(2026, 1, 15))
        fixture["forecast_intervals"][0]["delivery_start_utc"] = "2026-01-15T00:00:00"

        result, artifact = self.run_cli(fixture)

        self.assertEqual(result.returncode, 2)
        self.assertIsNone(artifact)
        self.assertIn("delivery_start_utc must be timezone-aware UTC", result.stderr)

    def test_wheel_supports_only_python_3_12(self) -> None:
        with (ROOT / "pyproject.toml").open("rb") as project_file:
            project = tomllib.load(project_file)

        self.assertEqual(project["project"]["requires-python"], ">=3.12,<3.13")

    def test_artifact_matches_checked_in_v1_schema(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/v1/issuance.schema.json").read_text(encoding="utf-8")
        )
        result, artifact = self.run_cli(fixture_for(date(2026, 1, 15)))

        self.assertEqual(result.returncode, 0, result.stderr)
        assert artifact is not None
        self.assertEqual(set(artifact), set(schema["required"]))
        self.assertEqual(
            set(artifact["intervals"][0]),
            set(schema["properties"]["intervals"]["items"]["required"]),
        )
        cardinalities = schema["properties"]["intervals"]["oneOf"]
        self.assertEqual(
            {(case["minItems"], case["maxItems"]) for case in cardinalities},
            {(92, 92), (96, 96), (100, 100)},
        )


if __name__ == "__main__":
    unittest.main()
