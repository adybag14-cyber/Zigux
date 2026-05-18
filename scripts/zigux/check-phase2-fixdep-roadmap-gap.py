#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY = ROOT / "Documentation" / "zigux" / "phase2-fixdep-roadmap-gap-survey.md"

SURVEY_MARKERS = (
    "Lane: `P2-L01`",
    "`scripts/basic/fixdep.c`",
    "`scripts/zigux/fixdep.zig`",
    "`wrapper-first path for parser-heavy tooling`",
    "`selected dual implementations`",
    "commit 11",
    "commit 13",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "live twelve-case fixture packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`zig test scripts/zigux/fixdep.zig`",
    "The current repo does not show a roadmap gap in the core dual-implementation requirement for `fixdep`",
    "The bounded remaining risk is reminder-surface drift, not missing parser work.",
)

EXPECTED_SELF_TEST_CASE_COUNT = len(SURVEY_MARKERS) + 2


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_missing_markers(text: str) -> list[str]:
    return [marker for marker in SURVEY_MARKERS if marker not in text]


def check_survey(root: Path) -> list[str]:
    survey_text = read_text(root / SURVEY.relative_to(ROOT))
    return collect_missing_markers(survey_text)


def emit_failures(missing_markers: list[str]) -> int:
    print("PHASE2_FIXDEP_ROADMAP_GAP=fail")
    print("PHASE2_FIXDEP_ROADMAP_GAP_MISSING_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("PHASE2_FIXDEP_ROADMAP_GAP_MISSING_MARKERS_END")
    return 1


def build_self_test_survey() -> str:
    return "# Phase 2 fixdep roadmap-gap survey\n\n" + "\n".join(f"- {marker}" for marker in SURVEY_MARKERS) + "\n"


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_fixdep_roadmap_gap_") as tmp_dir:
        root = Path(tmp_dir)
        survey_path = root / SURVEY.relative_to(ROOT)
        survey_path.parent.mkdir(parents=True, exist_ok=True)

        survey_path.write_text(build_self_test_survey(), encoding="utf-8")
        assert check_survey(root) == []
        checks_run += 1

        for marker in SURVEY_MARKERS:
            survey_path.write_text(build_self_test_survey().replace(f"- {marker}\n", "", 1), encoding="utf-8")
            missing = check_survey(root)
            assert marker in missing
            checks_run += 1

        survey_path.unlink()
        try:
            check_survey(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing survey did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_FIXDEP_ROADMAP_GAP_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_ROADMAP_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 fixdep roadmap-gap survey stays aligned with the current dual-implementation lane evidence."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_markers = check_survey(args.root)
    if missing_markers:
        return emit_failures(missing_markers)

    print("PHASE2_FIXDEP_ROADMAP_GAP=pass")
    print(f"PHASE2_FIXDEP_ROADMAP_GAP_MARKER_COUNT={len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
