# Methodology

## Training target

The model learns an effective residual acceleration:

`delta_acceleration = (v_teacher_next - v_quick_next) / dt`

This keeps the neural target tied to the truncation error of the quick integrator rather than the full physical state.

## Data generation

- Generalist data: synthetic orbital systems with a solar-mass primary and randomized secondary bodies.
- Specialist data: perturbations around a frozen Solar System or Apophis fixture.
- All states are standardized to barycentric coordinates and canonical body ordering.

## Safety-first evaluation

Loss alone is not treated as success. Every model must also be evaluated with:

- rollout error across multiple steps;
- energy drift;
- angular momentum drift;
- fallback frequency;
- runtime against the reference engine.

## OOD strategy

The v1.0 guard uses a diagonal Mahalanobis-like score over flattened state features with a threshold fitted from the training set. The design intentionally leaves room for MC dropout and ensemble disagreement in later versions.
