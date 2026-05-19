#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
SELF_PATH = Path("scripts/zigux/check-phase15-tests-readme-alignment.py")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
)

BROADER_GAP_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_MARKERS = (
    "## Phase 15 governance packet",
    "Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` explicit as the shipped reminder guards",
    "Current `master` does materialize `scripts/zigux/check-phase15-readiness-gate-packet.py`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_readiness_gate.zig`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `zigux/tests/phase15_indefinite_c_policy.zig`",
    "Current `master` still does not materialize `scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, or `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "the handoff manifest",
    "the focused handoff-note checker",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = _read(root / TESTS_README_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            failures.append(f"tests_readme:missing:{marker}")

    if f"`{SELF_PATH.as_posix()}`" not in readme:
        failures.append(f"tests_readme:missing_self_checker:`{SELF_PATH.as_posix()}`")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    if not (root / MAKEFILE_PATH).exists():
        failures.append(f"repo:missing_present_path:{MAKEFILE_PATH}")

    for rel in BROADER_GAP_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_gap_path:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    return failures


def _sample_readme() -> str:
    direct = ", ".join(f"`{rel}`" for rel in DIRECT_PACKET_PATHS)
    broader = ", ".join(f"`{rel}`" for rel in BROADER_GAP_PATHS)
    return f"""# zigux/tests

## Phase 15 governance packet

Keep the current directly readable Phase 15 reminder packet explicit through {direct}.

Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.

Current `master` does materialize `scripts/zigux/check-phase15-readiness-gate-packet.py`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_readiness_gate.zig`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `zigux/tests/phase15_indefinite_c_policy.zig`, so keep those returned readiness, handoff, shared-summary, handoff-note-checker, and stay-in-C packet members explicit in the tests-root reminder instead of leaving them in a missing-evidence bucket.

Current `master` still does not materialize `scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, or `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep those validator-first, route-level, build-level, handoff-replay, and lane-owner-alignment surfaces framed as repo-reality gaps unless fresh current-tree reads restore them.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet, the returned readiness and handoff survey packet members, the handoff manifest, the focused handoff-note checker, the shared-summary gap note, the active-governance replay entrypoints, and the still-missing validator-first, route-level, build-level, handoff-replay, and lane-owner-alignment surfaces aligned without promoting blocked governance wrappers or deeper-core status changes into current tests-root evidence?

Gap bucket: {broader}
"""


def _seed(root: Path) -> None:
    _write(root / TESTS_README_PATH, _sample_readme())
    for rel in DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")
    _write(root / MAKEFILE_PATH, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_tests_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_checker_root = root / "missing_checker"
        _seed(missing_checker_root)
        _write(
            missing_checker_root / TESTS_README_PATH,
            _sample_readme()
            .replace("`scripts/zigux/check-phase15-handoff-note-alignment.py`, ", "", 1)
            .replace(", `scripts/zigux/check-phase15-handoff-note-alignment.py`", "", 1),
        )
        failures = collect_failures(missing_checker_root)
        expected = [
            "tests_readme:missing:Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` explicit as the shipped reminder guards",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker failure: {failures}")

        missing_manifest_root = root / "missing_manifest"
        _seed(missing_manifest_root)
        (missing_manifest_root / "zigux/tests/phase15_handoff_next_steps_manifest.json").unlink()
        failures = collect_failures(missing_manifest_root)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_handoff_next_steps_manifest.json"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-manifest failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed(returned_gap_root)
        _write(returned_gap_root / BROADER_GAP_PATHS[0], "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")

    print("PHASE15_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 tests-root reminder stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())