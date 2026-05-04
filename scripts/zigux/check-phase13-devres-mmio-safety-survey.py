#!/usr/bin/env python3
"""Check the bounded Phase 13 devres MMIO/iomap safety survey packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_SUMMARY_BOOLEANS = {
    "preexisting_phase13_devres_iomap_reviewability_present": True,
}

REQUIRED_GAPS = {
    "phase13-devres-devicetree-iomap-planner": "starter_landed",
    "phase13-devres-live-mmio-side-effects": "blocked_on_live_mmio_state",
    "phase13-devres-live-device-tree-walk": "blocked_on_device_tree_state",
    "phase13-devres-live-arch-memtype-state": "blocked_on_arch_memtype_state",
}

REQUIRED_SURVEY_MARKERS = (
    "`devm_of_iomap()`",
    "live MMIO side effects",
    "live device-tree walking",
    "live MTRR or arch memtype state mutation",
)


class CheckError(RuntimeError):
    pass


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def check_packet(manifest_path: Path, survey_path: Path) -> None:
    manifest = load_manifest(manifest_path)
    survey_text = load_text(survey_path)

    require(manifest.get("phase") == "Phase 13", "manifest.phase must be 'Phase 13'")
    require(manifest.get("anchor") == "lib/devres.c", "manifest.anchor must be 'lib/devres.c'")

    summary = manifest.get("survey_summary")
    require(isinstance(summary, dict), "manifest.survey_summary must be an object")
    for key, expected in REQUIRED_SUMMARY_BOOLEANS.items():
        actual = summary.get(key)
        require(actual is expected, f"manifest.survey_summary.{key} must be {expected!r}, got {actual!r}")

    gaps = manifest.get("gaps")
    require(isinstance(gaps, list), "manifest.gaps must be a list")
    by_id = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, expected_status in REQUIRED_GAPS.items():
        gap = by_id.get(gap_id)
        require(gap is not None, f"missing manifest gap {gap_id}")
        actual_status = gap.get("status")
        require(
            actual_status == expected_status,
            f"manifest gap {gap_id} must have status {expected_status!r}, got {actual_status!r}",
        )

    for marker in REQUIRED_SURVEY_MARKERS:
        require(marker in survey_text, f"survey note missing marker {marker!r}")


def write_fixture(root: Path, *, include_iomap_summary: bool = True, survey_overrides: dict[str, str] | None = None) -> tuple[Path, Path]:
    manifest = {
        "phase": "Phase 13",
        "anchor": "lib/devres.c",
        "survey_summary": {
            "preexisting_phase13_devres_iomap_reviewability_present": include_iomap_summary,
        },
        "gaps": [
            {
                "id": "phase13-devres-devicetree-iomap-planner",
                "status": "starter_landed",
            },
            {
                "id": "phase13-devres-live-mmio-side-effects",
                "status": "blocked_on_live_mmio_state",
            },
            {
                "id": "phase13-devres-live-device-tree-walk",
                "status": "blocked_on_device_tree_state",
            },
            {
                "id": "phase13-devres-live-arch-memtype-state",
                "status": "blocked_on_arch_memtype_state",
            },
        ],
    }
    survey_text = "\n".join(
        (
            "# Phase 13 devres helper DMA/scatterlist boundary survey",
            "The current packet keeps `devm_of_iomap()` reviewable.",
            "What remains blocked:",
            "- live MMIO side effects",
            "- live device-tree walking",
            "- live MTRR or arch memtype state mutation",
        )
    )
    if survey_overrides:
        for old, new in survey_overrides.items():
            survey_text = survey_text.replace(old, new)

    manifest_path = root / "zigux/tests/phase13_devres_manifest.json"
    survey_path = root / "Documentation/zigux/phase13-devres-survey.md"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    survey_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    survey_path.write_text(survey_text + "\n", encoding="utf-8")
    return manifest_path, survey_path


def run_self_test() -> None:
    temp_root = Path(tempfile.mkdtemp(prefix="phase13-devres-mmio-check-"))
    try:
        manifest_path, survey_path = write_fixture(temp_root)
        check_packet(manifest_path, survey_path)

        missing_iomap_manifest, ok_survey = write_fixture(temp_root / "missing_iomap", include_iomap_summary=False)
        try:
            check_packet(missing_iomap_manifest, ok_survey)
        except CheckError as exc:
            require("preexisting_phase13_devres_iomap_reviewability_present" in str(exc), "missing-iomap failure mismatch")
        else:
            raise AssertionError("expected missing iomap summary failure")

        missing_gap_manifest, gap_survey = write_fixture(temp_root / "missing_gap")
        gap_data = load_manifest(missing_gap_manifest)
        gap_data["gaps"] = [gap for gap in gap_data["gaps"] if gap["id"] != "phase13-devres-live-device-tree-walk"]
        missing_gap_manifest.write_text(json.dumps(gap_data, indent=2) + "\n", encoding="utf-8")
        try:
            check_packet(missing_gap_manifest, gap_survey)
        except CheckError as exc:
            require("phase13-devres-live-device-tree-walk" in str(exc), "missing-gap failure mismatch")
        else:
            raise AssertionError("expected missing gap failure")

        ok_manifest, missing_survey_marker = write_fixture(
            temp_root / "missing_survey_marker",
            survey_overrides={"live MMIO side effects": "helper-only MMIO bookkeeping"},
        )
        try:
            check_packet(ok_manifest, missing_survey_marker)
        except CheckError as exc:
            require("live MMIO side effects" in str(exc), "missing-marker failure mismatch")
        else:
            raise AssertionError("expected missing survey marker failure")

        print("self-test: ok")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="path to zigux/tests/phase13_devres_manifest.json")
    parser.add_argument("--survey", type=Path, help="path to Documentation/zigux/phase13-devres-survey.md")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    return parser.parse_args()


def default_repo_paths(script_path: Path) -> tuple[Path, Path]:
    repo_root = script_path.resolve().parents[1]
    return (
        repo_root / "zigux/tests/phase13_devres_manifest.json",
        repo_root / "Documentation/zigux/phase13-devres-survey.md",
    )


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    default_manifest, default_survey = default_repo_paths(Path(__file__))
    manifest_path = args.manifest or default_manifest
    survey_path = args.survey or default_survey

    check_packet(manifest_path, survey_path)
    print("phase13 devres mmio survey check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
