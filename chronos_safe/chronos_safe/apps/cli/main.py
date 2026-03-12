"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from chronos_safe.config.settings import SETTINGS
from chronos_safe.data.specialist_generator import SpecialistGenerationConfig, generate_specialist_dataset
from chronos_safe.data.synthetic_generator import SyntheticGenerationConfig, generate_generalist_dataset
from chronos_safe.data.horizons_client import HorizonsClient
from chronos_safe.physics.quick_integrator import QuickIntegrator
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine
from chronos_safe.simulation.hybrid_engine import HybridEngine, load_torch_model
from chronos_safe.simulation.mission_apophis import ApophisValidationConfig, run_apophis_validation
from chronos_safe.simulation.rollout import RolloutConfig, run_hybrid_rollout
from chronos_safe.training.train_generalist import run_train_generalist
from chronos_safe.training.train_specialist import run_train_specialist
from chronos_safe.data.scalers import PhysicalScaler
from chronos_safe.models.ood_guard import OODGuard
from chronos_safe.utils.serialization import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chronos", description="CHRONOS-SAFE command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_generalist = subparsers.add_parser("generate-generalist")
    gen_generalist.add_argument("--output-dir", default=str(SETTINGS.data_root / "processed" / "generalist"))
    gen_generalist.add_argument("--num-samples", type=int, default=128)
    gen_generalist.add_argument("--min-bodies", type=int, default=2)
    gen_generalist.add_argument("--max-bodies", type=int, default=6)
    gen_generalist.add_argument("--dt-days", type=float, default=1.0)

    gen_specialist = subparsers.add_parser("generate-specialist")
    gen_specialist.add_argument("--output-dir", default=str(SETTINGS.data_root / "processed" / "specialist"))
    gen_specialist.add_argument("--fixture-name", default="apophis/apophis_fixture.json")
    gen_specialist.add_argument("--num-samples", type=int, default=64)
    gen_specialist.add_argument("--dt-days", type=float, default=1.0)

    train_generalist = subparsers.add_parser("train-generalist")
    train_generalist.add_argument("--dataset-dir", default=str(SETTINGS.data_root / "processed" / "generalist"))
    train_generalist.add_argument("--output-dir", default=str(SETTINGS.models_root / "checkpoints" / "generalist"))
    train_generalist.add_argument("--epochs", type=int, default=20)
    train_generalist.add_argument("--batch-size", type=int, default=16)

    train_specialist = subparsers.add_parser("train-specialist")
    train_specialist.add_argument("--dataset-dir", default=str(SETTINGS.data_root / "processed" / "specialist"))
    train_specialist.add_argument("--output-dir", default=str(SETTINGS.models_root / "checkpoints" / "specialist"))
    train_specialist.add_argument("--base-checkpoint", default=None)
    train_specialist.add_argument("--epochs", type=int, default=10)
    train_specialist.add_argument("--batch-size", type=int, default=16)

    simulate = subparsers.add_parser("simulate")
    simulate.add_argument("--fixture-name", default="apophis/apophis_fixture.json")
    simulate.add_argument("--steps", type=int, default=30)
    simulate.add_argument("--dt-days", type=float, default=1.0)
    simulate.add_argument("--checkpoint-path", default=None)
    simulate.add_argument("--scaler-path", default=None)
    simulate.add_argument("--ood-guard-path", default=None)
    simulate.add_argument("--output-path", default=str(SETTINGS.reports_root / "validation" / "simulation.json"))

    apophis = subparsers.add_parser("validate-apophis")
    apophis.add_argument("--steps", type=int, default=180)
    apophis.add_argument("--dt-days", type=float, default=1.0)
    apophis.add_argument("--checkpoint-path", default=None)
    apophis.add_argument("--scaler-path", default=None)
    apophis.add_argument("--ood-guard-path", default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "generate-generalist":
        generate_generalist_dataset(
            SyntheticGenerationConfig(
                output_dir=Path(args.output_dir),
                num_samples=args.num_samples,
                min_bodies=args.min_bodies,
                max_bodies=args.max_bodies,
                dt_days=args.dt_days,
            )
        )
        return
    if args.command == "generate-specialist":
        generate_specialist_dataset(
            SpecialistGenerationConfig(
                output_dir=Path(args.output_dir),
                fixture_name=args.fixture_name,
                num_samples=args.num_samples,
                dt_days=args.dt_days,
            )
        )
        return
    if args.command == "train-generalist":
        run_train_generalist(args.dataset_dir, args.output_dir, epochs=args.epochs, batch_size=args.batch_size)
        return
    if args.command == "train-specialist":
        run_train_specialist(
            args.dataset_dir,
            args.output_dir,
            base_checkpoint=args.base_checkpoint,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
        return
    if args.command == "simulate":
        client = HorizonsClient()
        initial_state = client.load_fixture(args.fixture_name)
        model = load_torch_model(args.checkpoint_path) if args.checkpoint_path else None
        scaler = PhysicalScaler.load(args.scaler_path) if args.scaler_path else None
        ood_guard = OODGuard.load(args.ood_guard_path) if args.ood_guard_path else None
        engine = HybridEngine(
            quick_integrator=QuickIntegrator(dt_days=args.dt_days),
            reference_engine=ReboundReferenceEngine(dt_days=args.dt_days, use_rebound=SETTINGS.use_rebound_if_available),
            model=model,
            scaler=scaler,
            ood_guard=ood_guard,
        )
        result = run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=args.steps, dt_days=args.dt_days))
        write_json(args.output_path, result.to_dict())
        return
    if args.command == "validate-apophis":
        run_apophis_validation(
            ApophisValidationConfig(
                steps=args.steps,
                dt_days=args.dt_days,
                checkpoint_path=None if args.checkpoint_path is None else Path(args.checkpoint_path),
                scaler_path=None if args.scaler_path is None else Path(args.scaler_path),
                ood_guard_path=None if args.ood_guard_path is None else Path(args.ood_guard_path),
            )
        )
        return


if __name__ == "__main__":
    main()
