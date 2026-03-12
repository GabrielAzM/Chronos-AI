from pathlib import Path

from chronos_safe.data.specialist_generator import SpecialistGenerationConfig, generate_specialist_dataset
from chronos_safe.data.synthetic_generator import SyntheticGenerationConfig, generate_generalist_dataset


def test_generalist_generator_persists_dataset(tmp_path: Path) -> None:
    output_dir = tmp_path / "generalist"
    generate_generalist_dataset(SyntheticGenerationConfig(output_dir=output_dir, num_samples=8, min_bodies=2, max_bodies=3))
    assert (output_dir / "dataset.npz").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "scaler.json").exists()


def test_specialist_generator_persists_dataset(tmp_path: Path) -> None:
    output_dir = tmp_path / "specialist"
    generate_specialist_dataset(SpecialistGenerationConfig(output_dir=output_dir, num_samples=6))
    assert (output_dir / "dataset.npz").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "scaler.json").exists()
