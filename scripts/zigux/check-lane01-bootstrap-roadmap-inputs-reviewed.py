#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

REQUIRED_LINES = (
    "## Inputs Reviewed",
    "The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:",
    "- `zigux_bundle_review_v2.csv`",
    "- `zigux_full_parity_focus_v2.csv`",
    "- `zigux_linux_to_zigux_map_v2.csv`",
    "- `zigux_master_phases_v2.csv`",
    "- `zigux_phase_targets_v2.csv`",
    "- `zigux_pm_roadmap_v2.xlsx`",
    "- `zigux_risk_register_v2.csv`",
    "- `zigux_sources_v2.csv`",
    "- `zigux_structure_v2.csv`",
    "- `zigux_workstreams_v2.csv`",
    "I also checked the current public repo state at:",
    "- <https://github.com/adybag14-cyber/Zigux>",
)

ORDERED_HEADINGS = (
    "## Purpose",
    "## Bootstrap Status Note",
    "## Inputs Reviewed",
    "## Bundle Normalization Notes",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    roadmap_path = root / ROADMAP_PATH
    if not roadmap_path.exists():
        return [f"missing_file:{ROADMAP_PATH.as_posix()}"]

    roadmap = _read(roadmap_path)
    failures: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            failures.append(f"missing:{line}")

    positions: list[int] = []
    missing_headings = False
    for heading in ORDERED_HEADINGS:
        position = roadmap.find(heading)
        if position == -1:
            failures.append(f"missing:{heading}")
            missing_headings = True
        positions.append(position)

    if not missing_headings and positions != sorted(positions):
        failures.append(
            "order:Purpose->BootstrapStatusNote->InputsReviewed->BundleNormalizationNotes"
        )

    return failures


def _sample_roadmap() -> str:
    lines = [
        "# ZAR to Zigux Product Roadmap",
        "",
        "## Purpose",
        "",
        "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.",
        "",
        "## Bootstrap Status Note",
        "",
        "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
        "",
        "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
        "",
        "## Inputs Reviewed",
        "",
        "The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:",
        "- `zigux_bundle_review_v2.csv`",
        "- `zigux_full_parity_focus_v2.csv`",
        "- `zigux_linux_to_zigux_map_v2.csv`",
        "- `zigux_master_phases_v2.csv`",
        "- `zigux_phase_targets_v2.csv`",
        "- `zigux_pm_roadmap_v2.xlsx`",
        "- `zigux_risk_register_v2.csv`",
        "- `zigux_sources_v2.csv`",
        "- `zigux_structure_v2.csv`",
        "- `zigux_workstreams_v2.csv`",
        "",
        "I also checked the current public repo state at:",
        "- <https://github.com/adybag14-cyber/Zigux>",
        "",
        "## Bundle Normalization Notes",
        "",
        "Placeholder section for focused Lane 01 checker validation.",
        "",
    ]
    return "\n".join(lines)


def write_sample_root(root: Path) -> None:
    _write(root / ROADMAP_PATH, _sample_roadmap())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_inputs_reviewed_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_failures(root):
            raise AssertionError("baseline Inputs Reviewed fixture should pass")
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `zigux_pm_roadmap_v2.xlsx`\n", "", 1),
        )
        failures = collect_failures(root)
        expected = ["missing:- `zigux_pm_roadmap_v2.xlsx`"]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for missing workbook entry case: {failures}"
            )
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- <https://github.com/adybag14-cyber/Zigux>\n", "", 1
            ),
        )
        failures = collect_failures(root)
        expected = ["missing:- <https://github.com/adybag14-cyber/Zigux>"]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for missing repo link case: {failures}"
            )
        write_sample_root(root)
        case_count += 1

        reordered = _sample_roadmap().replace(
            "\n## Inputs Reviewed\n\nThe roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:\n- `zigux_bundle_review_v2.csv`\n- `zigux_full_parity_focus_v2.csv`\n- `zigux_linux_to_zigux_map_v2.csv`\n- `zigux_master_phases_v2.csv`\n- `zigux_phase_targets_v2.csv`\n- `zigux_pm_roadmap_v2.xlsx`\n- `zigux_risk_register_v2.csv`\n- `zigux_sources_v2.csv`\n- `zigux_structure_v2.csv`\n- `zigux_workstreams_v2.csv`\n\nI also checked the current public repo state at:\n- <https://github.com/adybag14-cyber/Zigux>\n\n## Bundle Normalization Notes\n",
            "\n## Bundle Normalization Notes\n\n## Inputs Reviewed\n\nThe roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:\n- `zigux_bundle_review_v2.csv`\n- `zigux_full_parity_focus_v2.csv`\n- `zigux_linux_to_zigux_map_v2.csv`\n- `zigux_master_phases_v2.csv`\n- `zigux_phase_targets_v2.csv`\n- `zigux_pm_roadmap_v2.xlsx`\n- `zigux_risk_register_v2.csv`\n- `zigux_sources_v2.csv`\n- `zigux_structure_v2.csv`\n- `zigux_workstreams_v2.csv`\n\nI also checked the current public repo state at:\n- <https://github.com/adybag14-cyber/Zigux>\n",
            1,
        )
        _write(root / ROADMAP_PATH, reordered)
        failures = collect_failures(root)
        expected = [
            "order:Purpose->BootstrapStatusNote->InputsReviewed->BundleNormalizationNotes"
        ]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for reordered heading case: {failures}"
            )
        write_sample_root(root)
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("## Inputs Reviewed\n\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "missing:## Inputs Reviewed",
            "missing:## Inputs Reviewed",
        ]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for missing heading case: {failures}"
            )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap keeps the Inputs Reviewed packet aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic roadmap fixtures",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root for focused local validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"Wrote sample root to {args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED=fail")
        for failure in failures:
            print(f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_FAILURE={failure}")
        return 1

    print("Lane 01 roadmap Inputs Reviewed check passed.")
    print("LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED=pass")
    print(
        f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}"
    )
    print(
        "LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SECTION_ORDER="
        "Purpose->BootstrapStatusNote->InputsReviewed->BundleNormalizationNotes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
