# delu

Portable DE-LU Day-Ahead electricity price forecast contracts.

## Local tracer

Use Python 3.12 and pass a complete JSON input to the wheel entry point:

```sh
uv run delu emit-day-ahead input.json artifact.json
```

The input contains issuance clocks and provenance plus one forecast for every
UTC quarter hour in the requested Europe/Berlin Market Delivery Day. Each
forecast must contain `delivery_start_utc`, `point`, `q10`, `q25`, `q50`,
`q75`, and `q90`. The contract tests construct ordinary, spring-transition,
and autumn-transition examples in `tests/test_forecast_cli.py`.

The output follows `schemas/v1/issuance.schema.json`. Its `content_sha256` is
the SHA-256 of compact, key-sorted UTF-8 JSON after removing that checksum
field.

Run the default network-free test suite with:

```sh
uv run python -m unittest
```
