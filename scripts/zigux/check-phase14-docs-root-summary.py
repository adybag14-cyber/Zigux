#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

README_PATH = "Documentation/zigux/README.md"
RELEASE_SURVEY_PATH = "Documentation/zigux/phase14-release-boundary-survey.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"

README_MARKERS = [
    "Phase 14 notes",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`scripts/zigux/validate-phase14.py`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`zigux/tests/phase14_build.zig`",
    "validator-backed shared smoke gate",
    "study-only four-anchor packet",
    "reviewability lane rather than a closure or active subsystem delivery claim",
]

RELEASE_MARKERS = [
    "PHASE14_STATUS=study_only",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`scripts/zigux/validate-phase14.py`",
    "`zigux/tests/phase14_build.zig`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
]

SMOKE_MARKERS = [
    "PHASE14_STATUS=active",
    "PHASE14_SLICE=end-to-end-smoke-verification",
    "PHASE14_SHARED_LANE=P14-L01",
    "PHASE14_SMOKE_VALIDATOR=present",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
]


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def expect_markers(label: str, source: str, markers: list[str], missing: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> list[str]:
    missing: list[str] = []
    readme = read_text(root, README_PATH)
    release_survey = read_text(root, RELEASE_SURVEY_PATH)
    smoke_survey = read_text(root, SMOKE_SURVEY_PATH)

    expect_markers("readme", readme, README_MARKERS, missing)
    expect_markers("release_survey", release_survey, RELEASE_MARKERS, missing)
    expect_markers("smoke_survey", smoke_survey, SMOKE_MARKERS, missing)

    stale_line = "there is no dedicated shared Phase 14 replay gate on current `master`"
    if stale_line in readme:
        missing.append("readme:stale_no_replay_gate_claim")

    phase14_shared_replay = "PHASE14_SHARED_REPLAY_PRESENT=yes"
    if phase14_shared_replay not in release_survey:
        missing.append("release_survey:shared_replay_present")

    if "validator-backed shared smoke gate" in readme and phase14_shared_replay not in release_survey:
        missing.append("cross_file:readme_claim_without_release_survey_marker")

    return missing


def run_self_test() -> int:
    fixture_root = Path(tempfile.mkdtemp(prefix="phase14_docs_root_checker_"))
    try:
        docs_root = fixture_root / "Documentation/zigux"
        docs_root.mkdir(parents=True)

        (docs_root / "README.md").write_text(
            """# Zigux Documentation

Phase 14 notes
- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now keep the roadmap's core-adjacent sequencing explicit from the docs root.
- `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` remain bounded to study-only and freeze-in-C posture.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.
""",
            encoding="utf-8",
        )
        (docs_root / "phase14-release-boundary-survey.md").write_text(
            """# Phase 14 Release Boundary Survey
- PHASE14_STATUS=study_only
- PHASE14_SHARED_REPLAY_PRESENT=yes
- PHASE14_SHARED_SMOKE_GATE_COUNT=1
- PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `scripts/zigux/validate-phase14.py`
- `zigux/tests/phase14_build.zig`
- `make -C zigux phase14-validate`
- `make -C zigux phase14-smoke`
""",
            encoding="utf-8",
        )
        (docs_root / "phase14-end-to-end-smoke-survey.md").write_text(
            """# Phase 14 End-to-End Smoke Survey
- PHASE14_STATUS=active
- PHASE14_SLICE=end-to-end-smoke-verification
- PHASE14_SHARED_LANE=P14-L01
- PHASE14_SMOKE_VALIDATOR=present
- PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate
- PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all
- PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14
""",
            encoding="utf-8",
        )

        missing = validate(fixture_root)
        if missing:
            print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST=fail")
            print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST_MISSING_START")
            for item in missing:
                print(item)
            print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST_MISSING_END")
            return 1

        stale_readme = docs_root / "README.md"
        stale_readme.write_text(
            stale_readme.read_text(encoding="utf-8").replace(
                "validator-backed shared smoke gate",
                "there is no dedicated shared Phase 14 replay gate on current `master`",
            ),
            encoding="utf-8",
        )
        stale_missing = validate(fixture_root)
        if "readme:stale_no_replay_gate_claim" not in stale_missing:
            print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST=fail")
            print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST_EXPECTED_STALE_CLAIM=missing")
            return 1

        print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST=pass")
        print("PHASE14_DOCS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT=2")
        return 0
    finally:
        shutil.rmtree(fixture_root, ignore_errors=True)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        return run_self_test()
    if len(argv) != 1:
        print("usage: check-phase14-docs-root-summary.py [--self-test]", file=sys.stderr)
        return 2

    missing = validate(ROOT)
    if missing:
        print("PHASE14_DOCS_ROOT_SUMMARY=fail")
        print("PHASE14_DOCS_ROOT_SUMMARY_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE14_DOCS_ROOT_SUMMARY_MISSING_END")
        return 1

    print("PHASE14_DOCS_ROOT_SUMMARY=pass")
    print(f"PHASE14_DOCS_ROOT_SUMMARY_MARKER_COUNT={len(README_MARKERS) + len(RELEASE_MARKERS) + len(SMOKE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
