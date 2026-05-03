#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40_NOTE = "survey provenance captured against verified `master` head"

DOCS_ROOT_LINES = [
    "Phase 14 notes",
    "`Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture",
    "`kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate",
    "reviewability lane rather than a closure or active subsystem delivery claim",
]

SURVEY_LINES = [
    "PHASE14_SHARED_LANE=P14-L01",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zigux/tests/phase14_build.zig",
    "reviewability lane rather than a closure or active subsystem delivery claim",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_markers(label: str, text: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")
    return missing


def validate_docs_root(docs_root_text: str, survey_text: str) -> list[str]:
    missing = require_markers("docs_root", docs_root_text, DOCS_ROOT_LINES)
    missing.extend(require_markers("survey", survey_text, SURVEY_LINES))
    if HEX40_NOTE not in survey_text:
        missing.append(f"survey:{HEX40_NOTE}")
    return missing


def run_self_test() -> int:
    docs_root_text = """
Phase 14 notes
- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root, so release-facing review no longer jumps directly from the active Phase 13 helper tranche to the Phase 15 governance packet.
- the current Phase 14 release reading is intentionally boundary-only: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture, while `kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet rather than being treated as an active release lane.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.
""".strip()

    survey_text = """
- PHASE14_SHARED_LANE=P14-L01
- PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate
- survey provenance captured against verified `master` head `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- make -C zigux phase14-smoke
- zigux/tests/phase14_build.zig
- reviewability lane rather than a closure or active subsystem delivery claim
""".strip()

    cases = [
        ("happy_path", docs_root_text, survey_text, False),
        (
            "missing_docs_root_smoke_gate",
            docs_root_text.replace("validator-backed shared smoke gate", "shared smoke gate"),
            survey_text,
            True,
        ),
        (
            "missing_survey_entrypoint",
            docs_root_text,
            survey_text.replace("PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate", ""),
            True,
        ),
    ]

    for name, docs_text, survey_value, should_fail in cases:
        missing = validate_docs_root(docs_text, survey_value)
        failed = bool(missing)
        if failed != should_fail:
            print(f"PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST={name}:fail")
            if missing:
                print("MISSING_MARKERS_START")
                for marker in missing:
                    print(marker)
                print("MISSING_MARKERS_END")
            return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST=pass")
    print(f"PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    docs_root_path = ROOT / "Documentation/zigux/README.md"
    survey_path = ROOT / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"

    missing_files = [str(path) for path in (docs_root_path, survey_path) if not path.exists()]
    if missing_files:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    missing = validate_docs_root(read(docs_root_path), read(survey_path))
    if missing:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=pass")
    print(f"PHASE14_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_LINES)}")
    print(f"PHASE14_SURVEY_MARKER_COUNT={len(SURVEY_LINES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
