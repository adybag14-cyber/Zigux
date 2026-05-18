#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
READINESS_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"
HANDOFF_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
PARITY_SCORECARD_REL = "Documentation/zigux/phase15-parity-scorecard.md"
DOCS_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
SCRIPTS_CHECKER_REL = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
GAP_CHECKER_REL = "scripts/zigux/check-phase15-shared-summary-gap.py"
READINESS_CHECKER_REL = "scripts/zigux/check-phase15-readiness-gate-packet.py"
READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
REVIEW_PROCESS_MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
MAKEFILE_REL = "zigux/Makefile"

REQUIRED_FILES = (
    README_REL,
    TESTS_README_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    LANE_SEQ_REL,
    READINESS_REL,
    SHARED_GAP_REL,
    HANDOFF_REL,
    FREEZE_GOVERNANCE_REL,
    PARITY_SCORECARD_REL,
    DOCS_CHECKER_REL,
    SCRIPTS_CHECKER_REL,
    HANDOFF_CHECKER_REL,
    GAP_CHECKER_REL,
    READINESS_CHECKER_REL,
    READINESS_MANIFEST_REL,
    REVIEW_PROCESS_MANIFEST_REL,
    MAKEFILE_REL,
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
)

README_PHASE15_MARKERS = (
    "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

LANE_SEQ_MARKERS = (
    "`scripts/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
)

READINESS_MARKERS = (
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`zigux/Makefile`",
    "blocked route vocabulary",
)

SHARED_GAP_MARKERS = (
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
)

HANDOFF_MARKERS = (
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
)

FOCUSED_COMPANION_RELS = (
    "zigux/tests/phase15_architecture_council_review_process.zig",
    REVIEW_PROCESS_MANIFEST_REL,
    HANDOFF_CHECKER_REL,
)

MISSING_BROADER_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

STALE_PRESENT_ROUTE_MARKERS = (
    "directly readable replay paths",
    "shipped replay paths",
    "direct tests-root evidence",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    readme = _read(root / README_REL)
    lane_seq = _read(root / LANE_SEQ_REL)
    readiness = _read(root / READINESS_REL)
    shared_gap = _read(root / SHARED_GAP_REL)
    handoff = _read(root / HANDOFF_REL)
    makefile = _read(root / MAKEFILE_REL)

    _require_markers(readme, README_PHASE15_MARKERS, "readme_phase15", failures)
    _require_markers(lane_seq, LANE_SEQ_MARKERS, "lane_seq", failures)
    _require_markers(readiness, READINESS_MARKERS, "readiness", failures)
    _require_markers(shared_gap, SHARED_GAP_MARKERS, "shared_gap", failures)
    _require_markers(handoff, HANDOFF_MARKERS, "handoff", failures)

    for rel in FOCUSED_COMPANION_RELS:
        marker = f"`{rel}`"
        if marker not in shared_gap:
            failures.append(f"shared_gap:missing_materialized:{marker}")
        if not (root / rel).exists():
            failures.append(f"missing_materialized_file:{rel}")

    for rel in MISSING_BROADER_PATHS:
        marker = f"`{rel}`"
        if marker not in readiness:
            failures.append(f"readiness:missing_gap_path:{marker}")
        if marker not in shared_gap:
            failures.append(f"shared_gap:missing_gap_path:{marker}")
        if (root / rel).exists():
            failures.append(f"missing_gap_path_returned:{rel}")

    for marker in STALE_PRESENT_ROUTE_MARKERS:
        stale_phrase = f"keep those route names as {marker}"
        if stale_phrase in readme:
            failures.append(f"readme:stale_phase15_route_claim:{stale_phrase}")

    for marker in (
        "phase15-validate:",
        "phase15-test:",
        "phase15:",
        ".PHONY: phase15",
    ):
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    return failures


def _sample_readme() -> str:
    return """# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 13

- keep the shipped Phase 13 helper packet explicit.

## Phase 15

- Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` keep the shipped docs-root, scripts-root, handoff, shared-summary, and readiness packet guards explicit from the scripts root
- `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, and `zigux/tests/phase15_readiness_gate_manifest.json` keep the current directly readable governance packet explicit from the scripts root
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_build.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep those broader validator-first, handoff-manifest, build, and lane-owner companions framed as repo-reality gaps instead of shipped scripts-root evidence
- although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths
- no Architecture Council approval is currently recorded for a freeze-map status change, and any future follow-through should tighten the smallest truthful reminder surface first instead of widening into a status-change claim
"""


def _seed(root: Path) -> None:
    _write(root / README_REL, _sample_readme())
    _write(
        root / LANE_SEQ_REL,
        "# Phase 15 Governance Lane Sequencing\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `Documentation/zigux/review-checklist.md`\n"
        "- `Documentation/zigux/phase15-readiness-gate-survey.md`\n"
        "- `Documentation/zigux/phase15-handoff-next-steps-survey.md`\n",
    )
    _write(
        root / READINESS_REL,
        "# Phase 15 Readiness Gate Survey\n\n"
        "- `scripts/zigux/check-phase15-docs-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-scripts-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n"
        "- `scripts/zigux/validate-phase15.py`\n"
        "- `zigux/tests/phase15_handoff_next_steps_manifest.json`\n"
        "- `zigux/tests/phase15_build.zig`\n"
        "- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`\n"
        "- `zigux/Makefile`\n"
        "- broader replay remains blocked route vocabulary\n",
    )
    _write(
        root / SHARED_GAP_REL,
        "# Phase 15 Shared Summary Gap\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `scripts/zigux/check-phase15-docs-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n"
        "- `zigux/tests/phase15_readiness_gate_manifest.json`\n"
        "- `zigux/tests/phase15_architecture_council_review_process.zig`\n"
        "- `zigux/tests/phase15_architecture_council_review_process_manifest.json`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/validate-phase15.py`\n"
        "- `zigux/tests/phase15_handoff_next_steps_manifest.json`\n"
        "- `zigux/tests/phase15_build.zig`\n"
        "- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`\n"
        "- parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes\n",
    )
    _write(
        root / HANDOFF_REL,
        "# Phase 15 Handoff Next Steps Survey\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `zigux/tests/README.md`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n",
    )
    _write(
        root / MAKEFILE_REL,
        "PYTHON ?= python3\n"
        ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2\n"
        "phase2-toolchain:\n"
        "\t@true\n",
    )
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            _write(root / rel, "placeholder\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_scripts_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_phase15_marker = root / "missing_phase15_marker"
        _seed(missing_phase15_marker)
        _write(
            missing_phase15_marker / README_REL,
            _sample_readme().replace("`Documentation/zigux/phase15-governance-lane-sequencing.md`, ", "", 1),
        )
        failures = validate(missing_phase15_marker)
        expected = [
            "readme_phase15:missing:`Documentation/zigux/phase15-governance-lane-sequencing.md`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-phase15-marker failure: {failures}")

        stale_claim = root / "stale_claim"
        _seed(stale_claim)
        _write(
            stale_claim / README_REL,
            _read(stale_claim / README_REL).replace(
                "keep those route names as blocked route vocabulary rather than directly readable replay paths",
                "keep those route names as directly readable replay paths",
                1,
            ),
        )
        failures = validate(stale_claim)
        expected = [
            "readme_phase15:missing:although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths",
            "readme:stale_phase15_route_claim:keep those route names as directly readable replay paths",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-claim failure: {failures}")

        returned_gap = root / "returned_gap"
        _seed(returned_gap)
        _write(returned_gap / "scripts/zigux/validate-phase15.py", "present\n")
        failures = validate(returned_gap)
        expected = ["missing_gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

        route_returned = root / "route_returned"
        _seed(route_returned)
        _write(route_returned / MAKEFILE_REL, _read(route_returned / MAKEFILE_REL) + "\nphase15-validate:\n\t@true\n")
        failures = validate(route_returned)
        expected = ["makefile:unexpected_phase15_route:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile-route failure: {failures}")

        missing_marker = root / "missing_marker"
        _seed(missing_marker)
        _write(missing_marker / HANDOFF_REL, "# Phase 15 Handoff Next Steps Survey\n")
        failures = validate(missing_marker)
        expected = [f"handoff:missing:{marker}" for marker in HANDOFF_MARKERS]
        if failures != expected:
            raise AssertionError(f"unexpected handoff-marker failure: {failures}")

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 scripts-root reminder stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
