#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_NOTE_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
READINESS_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
STUDY_ONLY_ACCOUNTING_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
REVIEW_PROCESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-process-handoff.py")
SELF_PATH = Path("scripts/zigux/check-phase15-tests-readme-alignment.py")
REVIEW_PROCESS_TEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
REVIEW_PROCESS_MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
READINESS_MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
)

BROADER_GAP_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/Makefile",
)

REQUIRED_MARKERS = (
    "Phase 15 review packet",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "`python3 scripts/zigux/check-phase15-tests-readme-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase15-review-process-handoff.py --self-test`",
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

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in BROADER_GAP_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_gap_path:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    return failures


def _sample_readme() -> str:
    direct = "\n".join(f"  * `{rel}`" for rel in DIRECT_PACKET_PATHS)
    broader = "\n".join(f"  * `{rel}`" for rel in BROADER_GAP_PATHS)
    return f"""# zigux/tests

Phase 15 review packet
  * current direct-readback Phase 15 governance packet:
{direct}
  * `python3 scripts/zigux/check-phase15-tests-readme-alignment.py --self-test` and `python3 scripts/zigux/check-phase15-review-process-handoff.py --self-test` replay the focused tests-root governance checks, while the live checker routes keep the shipped reminder packet honest without rebuilding the missing broader validator-first or build packet
  * repeated authenticated contents reads on current `master` still return missing for:
{broader}
  * keep the current Phase 15 tests-root reminder aligned with the directly materialized governance packet, including the dedicated Architecture Council review-process note and the study-only accounting note, instead of implying that the broader validator-first, handoff-manifest, build, lane-owner, or make-wrapper routes are already shipped on current `master`
  * no Architecture Council approval is currently recorded for a freeze-map status change, keep the four freeze-in-C anchors parked, keep the two roadmap study-only anchors parked, and keep any future follow-through narrowed to the smallest reminder-surface repair first
"""


def _seed(root: Path) -> None:
    _write(root / TESTS_README_PATH, _sample_readme())
    for rel in DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_tests_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_marker_root = root / "missing_marker"
        _seed(missing_marker_root)
        _write(
            missing_marker_root / TESTS_README_PATH,
            _sample_readme().replace(
                "  * `python3 scripts/zigux/check-phase15-tests-readme-alignment.py --self-test` and `python3 scripts/zigux/check-phase15-review-process-handoff.py --self-test` replay the focused tests-root governance checks, while the live checker routes keep the shipped reminder packet honest without rebuilding the missing broader validator-first or build packet\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "tests_readme:missing:`python3 scripts/zigux/check-phase15-tests-readme-alignment.py --self-test`",
            "tests_readme:missing:`python3 scripts/zigux/check-phase15-review-process-handoff.py --self-test`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed(missing_direct_root)
        (missing_direct_root / REVIEW_PROCESS_TEST_PATH).unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_architecture_council_review_process.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        returned_gap_root = root / "returned_gap"
        _seed(returned_gap_root)
        _write(returned_gap_root / "zigux/Makefile", "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:zigux/Makefile"]
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
