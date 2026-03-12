# Architecture

CHRONOS-SAFE is organized around four operational layers:

1. Physics layer: canonical state representation, barycentric transforms, invariant monitoring, quick integrator and trusted reference engine.
2. Data layer: offline-first fixtures, synthetic generalist generation, specialist perturbation generation, preprocessing and scaling.
3. Learning layer: residual GNN, OOD scoring and supervised training in two phases.
4. Runtime layer: hybrid rollout, safety guard, fallback orchestration, benchmarks and interfaces.

The primary runtime contract is `SystemState`, which carries `ids`, `masses`, `positions`, `velocities` and metadata.

Hybrid stepping follows this sequence:

1. Quick integrator proposes a step.
2. Residual GNN predicts `delta_acceleration`.
3. Candidate corrected state is assembled.
4. Safety guard validates the proposal.
5. If safe, the corrected state is accepted.
6. If unsafe, the system falls back to the reference engine and logs a `FallbackEvent`.
