#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
ARCHITECTURE_NOTE_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
GAP_NOTE_PATH = Path("Documentation/zigux/phase15-scripts-root-tooling-gap.md")

DOCS_MARKERS = (
    "Phase 15 notes",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)

TESTS_MARKERS = (
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)

ALIGNMENT_CHECKER_MARKERS = (
    "README_MARKERS = (",
    "\"Phase 15 flow\"",
    "\"make -C zigux phase15-validate\"",
    "\"make -C zigux phase15-test\"",
    "\"make -C zigux phase15\"",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
)

REQUIRED_GAP_NOTE_MARKERS = (
    "`PHASE15_STATUS=scripts_root_tooling_gap_recorded`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`Documentation/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
)

MISSING_PACKET_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def collect_gap_failures(root: Path) -> list[str]:
    docs_readme = _read(root / DOCS_README_PATH)
    tests_readme = _read(root / TESTS_README_PATH)
    scripts_readme = _read(root / SCRIPTS_README_PATH)
    alignment_checker = _read(root / ALIGNMENT_CHECKER_PATH)
    architecture_note = _read(root / ARCHITECTURE_NOTE_PATH)
    gap_note = _read(root / GAP_NOTE_PATH)

    failures: list[str] = []

    _require_markers(docs_readme, DOCS_MARKERS, "docs_readme", failures)
    _require_markers(tests_readme, TESTS_MARKERS, "tests_readme", failures)
    _require_markers(alignment_checker, ALIGNMENT_CHECKER_MARKERS, "alignment_checker", failures)
    _require_markers(gap_note, REQUIRED_GAP_NOTE_MARKERS, "gap_note", failures)

    if "Phase 15 flow" in scripts_readme:
        failures.append("scripts_readme:stale_gap:Phase 15 flow is now present and the tooling-gap note should be narrowed")

    if "no Architecture Council approval is currently recorded for a freeze-map status change" not in architecture_note:
        failures.append("architecture_note:missing:no-approval marker")

    for relative_path in MISSING_PACKET_PATHS:
        if (root / relative_path).exists():
            failures.append(f"missing_packet:materialized:{relative_path}")

    return failures


def _sample_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "",
            "Phase 15 notes",
            "- `scripts/zigux/check-phase15-scripts-readme-alignment.py`",
            "- `make -C zigux phase15-validate`",
            "- `make -C zigux phase15-test`",
            "- `make -C zigux phase15`",
            "",
        )
    )


def _sample_tests_readme() -> str:
    return "\n".join(
        (
            "# zigux/tests",
            "",
            "Phase 15 review packet",
            "- `scripts/zigux/check-phase15-scripts-readme-alignment.py`",
            "- `make -C zigux phase15-validate`",
            "- `make -C zigux phase15-test`",
            "- `make -C zigux phase15`",
            "",
        )
    )


def _sample_scripts_readme() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "## Phase 12",
            "- current scripts-root reminder packet",
            "",
        )
    )


def _sample_alignment_checker() -> str:
    return "\n".join(
        (
            "README_MARKERS = (",
            '    "Phase 15 flow",',
            '    "make -C zigux phase15-validate",',
            '    "make -C zigux phase15-test",',
            '    "make -C zigux phase15",',
            ")",
            'REQUIRED_FILES = ("scripts/zigux/validate-phase15.py", "zigux/tests/phase15_build.zig", "zigux/tests/phase15_architecture_council_review_process_manifest.json")',
            "",
        )
    )


def _sample_architecture_note() -> str:
    return "\n".join(
        (
            "# Phase 15 Architecture Council Review Process",
            "",
            "no Architecture Council approval is currently recorded for a freeze-map status change",
            "",
        )
    )


def _sample_gap_note() -> str:
    return "\n".join(
        (
            "# Phase 15 Scripts-Root Tooling Gap",
            "",
            "`PHASE15_STATUS=scripts_root_tooling_gap_recorded`",
            "`scripts/zigux/README.md`",
            "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
            "`scripts/zigux/validate-phase15.py`",
            "`zigux/tests/phase15_build.zig`",
            "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
            "`Documentation/zigux/README.md`",
            "`zigux/tests/README.md`",
            "`Documentation/zigux/phase15-architecture-council-review-process.md`",
            "",
        )
    )


def _seed_gap_layout(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / TESTS_README_PATH, _sample_tests_readme())
    _write(root / SCRIPTS_README_PATH, _sample_scripts_readme())
    _write(root / ALIGNMENT_CHECKER_PATH, _sample_alignment_checker())
    _write(root / ARCHITECTURE_NOTE_PATH, _sample_architecture_note())
    _write(root / GAP_NOTE_PATH, _sample_gap_note())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_gap_layout(root)
        failures = collect_gap_failures(root)
        if failures:
            raise AssertionError(f"baseline gap fixture should pass: {failures}")

        scripts_root = root / "scripts_present"
        _seed_gap_layout(scripts_root)
        _write(
            scripts_root / SCRIPTS_README_PATH,
            "# scripts/zigux\n\nPhase 15 flow\n",
        )
        failures = collect_gap_failures(scripts_root)
        if len(failures) != 1 or "scripts_readme:stale_gap" not in failures[0]:
            raise AssertionError(f"scripts-readme materialization failure missing expected marker: {failures}")

        packet_root = root / "packet_present"
        _seed_gap_layout(packet_root)
        _write(packet_root / "scripts/zigux/validate-phase15.py", "print('validator')\n")
        failures = collect_gap_failures(packet_root)
        if len(failures) != 1 or "missing_packet:materialized:scripts/zigux/validate-phase15.py" not in failures[0]:
            raise AssertionError(f"packet materialization failure missing expected marker: {failures}")

        docs_root = root / "docs_missing"
        _seed_gap_layout(docs_root)
        _write(docs_root / DOCS_README_PATH, "# Zigux Documentation\n")
        failures = collect_gap_failures(docs_root)
        if len(failures) != len(DOCS_MARKERS) or not all(failure.startswith("docs_readme:missing:") for failure in failures):
            raise AssertionError(f"docs marker failure missing expected markers: {failures}")

    print("PHASE15_SCRIPTS_ROOT_TOOLING_GAP_SELF_TEST=pass")
    print("PHASE15_SCRIPTS_ROOT_TOOLING_GAP_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 scripts-root tooling-gap note still matches current "
            "docs-root, tests-root, scripts-root, and repo-reality drift."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 tooling packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo layouts",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_gap_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 scripts-root tooling-gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
