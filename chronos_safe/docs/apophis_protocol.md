# Apophis Protocol

## v1.0 protocol

- Fixture: `data/fixtures/apophis/apophis_fixture.json`
- Horizon: `180 days`
- Step size: `1 day`
- Bodies: `Sun`, `Earth`, `Apophis`
- Outputs: JSON report and text summary in `reports/validation/`

## Procedure

1. Load the frozen offline fixture.
2. Run the reference engine rollout.
3. Run the hybrid rollout with safety fallback enabled.
4. Compare trajectories and Earth-Apophis distance.
5. Save drift, error, fallback and runtime metrics.

## Important caveat

The included fixture is a regression artifact, not a final ephemeris product. It is intended to validate software behavior and compare hybrid vs baseline execution paths in a reproducible way.
