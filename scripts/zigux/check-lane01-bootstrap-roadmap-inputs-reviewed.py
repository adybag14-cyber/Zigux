#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

EXPECTED_ARTIFACTS = (
    "zigux_bundle_review_v2.csv",
    "zigux_full_parity_focus_v2.csv",
    "zigux_linux_to_zigux_map_v2.csv",
    "zigux_master_phases_v2.csv",
    "zigux_phase_targets_v2.csv",
    "zigux_pm_roadmap_v2.xlsx",
    "zigux_risk_register_v2.csv",
    "zigux_sources_v2.csv",
    "zigux_structure_v2.csv",
    "zigux_workstreams_v2.csv",
)

EXPECTED_SECTION_ORDER = (
    "## Purpose",
    "## Bootstrap Status Note",
    "## Inputs Reviewed",
    "## Bundle Normalization Notes",
)

EXPECTED_SELF_TEST_CASES = (
    "baseline_round_trip",
    "missing_roadmap_file",
    "missing_inputs_heading",
    "missing_artifact_marker",
    "artifact_count_drift",
    "missing_repo_state_intro",
    "missing_repo_url",
    "section_order_drift",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(old)
    return text.replace(old, new, 1)


def section_slice(text: str, start_heading: str, end_heading: str) -> str:
    start = text.find(start_heading)
    end = text.find(end_heading)
    if start == -1 or end == -1 or start >= end:
        return ""
    return text[start:end]


def collect_failures(root: Path) -> list[str]:
    roadmap = root / ROADMAP_PATH
    if not roadmap.exists():
        return [f"missing_required_path:{ROADMAP_PATH}"]

    text = read_text(roadmap)
    failures: list[str] = []

    positions: list[tuple[str, int]] = []
    for heading in EXPECTED_SECTION_ORDER:
        pos = text.find(heading)
        if pos == -1:
            failures.append(f"missing_heading:{heading}")
        positions.append((heading, pos))

    if not failures:
        if any(positions[i][1] >= positions[i + 1][1] for i in range(len(positions) - 1)):
            failures.append("section_order_drift:Purpose->BootstrapStatusNote->InputsReviewed->BundleNormalizationNotes")

    reviewed = section_slice(text, "## Inputs Reviewed", "## Bundle Normalization Notes")
    if not reviewed:
        failures.append("inputs_reviewed_section_unreadable")
        return failures

    intro = "The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:"
    if intro not in reviewed:
        failures.append(f"missing_intro:{intro}")

    expected_artifact_lines = [f"- `{name}`" for name in EXPECTED_ARTIFACTS]
    for marker in expected_artifact_lines:
        if marker not in reviewed:
            failures.append(f"missing_artifact:{marker}")

    artifact_lines_before_repo = []
    for line in reviewed.splitlines():
        stripped = line.strip()
        if stripped == "I also checked the current public repo state at:":
            break
        if stripped.startswith("- `"):
            artifact_lines_before_repo.append(stripped)
    if len(artifact_lines_before_repo) != len(EXPECTED_ARTIFACTS):
        failures.append(
            "artifact_count_drift:"
            f"expected_{len(EXPECTED_ARTIFACTS)}_got_{len(artifact_lines_before_repo)}"
        )

    repo_intro = "I also checked the current public repo state at:"
    if repo_intro not in reviewed:
        failures.append(f"missing_repo_state_intro:{repo_intro}")

    repo_url = "- <https://github.com/adybag14-cyber/Zigux>"
    if repo_url not in reviewed:
        failures.append(f"missing_repo_url:{repo_url}")

    return failures


def sample_roadmap() -> str:
    artifact_lines = "\n".join(f"- `{name}`" for name in EXPECTED_ARTIFACTS)
    return f"""# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

## Bootstrap Status Note

This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.

For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:
{artifact_lines}

I also checked the current public repo state at:
- <https://github.com/adybag14-cyber/Zigux>

## Bundle Normalization Notes

Normalized counts from the extracted structured files:
- phases: `15`
"""


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        roadmap = root / ROADMAP_PATH
        baseline = sample_roadmap()
        write_text(roadmap, baseline)

        cases: list[tuple[str, str, str | None]] = [
            ("baseline_round_trip", baseline, None),
            ("missing_roadmap_file", "", "missing_required_path"),
            ("missing_inputs_heading", baseline.replace("## Inputs Reviewed", "## Reviewed Inputs", 1), "missing_heading"),
            (
                "missing_artifact_marker",
                baseline.replace("- `zigux_pm_roadmap_v2.xlsx`\n", "", 1),
                "missing_artifact",
            ),
            (
                "artifact_count_drift",
                baseline.replace(
                    "- `zigux_workstreams_v2.csv`\n",
                    "- `zigux_workstreams_v2.csv`\n- `zigux_extra_packet.csv`\n",
                    1,
                ),
                "artifact_count_drift",
            ),
            (
                "missing_repo_state_intro",
                baseline.replace("I also checked the current public repo state at:\n", "", 1),
                "missing_repo_state_intro",
            ),
            (
                "missing_repo_url",
                baseline.replace("- <https://github.com/adybag14-cyber/Zigux>\n", "", 1),
                "missing_repo_url",
            ),
            (
                "section_order_drift",
                baseline.replace(
                    "## Bootstrap Status Note\n\nThis roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n\nFor later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n\n## Inputs Reviewed",
                    "## Inputs Reviewed\n\nThe roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:\n"
                    + "\n".join(f"- `{name}`" for name in EXPECTED_ARTIFACTS)
                    + "\n\nI also checked the current public repo state at:\n- <https://github.com/adybag14-cyber/Zigux>\n\n## Bootstrap Status Note",
                    1,
                ),
                "section_order_drift",
            ),
        ]

        for name, content, expected in cases:
            if name == "missing_roadmap_file":
                if roadmap.exists():
                    roadmap.unlink()
            else:
                write_text(roadmap, content)
            failures = collect_failures(root)
            if expected is None:
                if failures:
                    raise SystemExit(f"{name} failed unexpectedly: {failures}")
            else:
                if not any(expected in failure for failure in failures):
                    raise SystemExit(f"{name} did not raise {expected}: {failures}")

    print("LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SELF_TEST_CASES={len(EXPECTED_SELF_TEST_CASES)}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = collect_failures(Path(args.root))
    if failures:
        for failure in failures:
            print(f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_FAIL={failure}")
        return 1

    print("Lane 01 bootstrap roadmap Inputs Reviewed check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_REQUIRED_ARTIFACT_COUNT={len(EXPECTED_ARTIFACTS)}")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_INPUTS_REVIEWED_SECTION_ORDER="
        "Purpose->BootstrapStatusNote->InputsReviewed->BundleNormalizationNotes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
