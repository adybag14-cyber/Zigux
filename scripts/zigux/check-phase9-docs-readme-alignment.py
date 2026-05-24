#!/usr/bin/env python3
"""Guard the shared Phase 9 docs-root reminder packet.

This checker is intentionally narrow. It verifies that the primary
`Phase 9 notes - ...` line in `Documentation/zigux/README.md` keeps the
current shared reminder surfaces explicit, including the dedicated
trace-events runtime packet guard.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile


DEFAULT_README = pathlib.Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "samples/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
)


def _extract_phase9_notes_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Phase 9 notes - "):
            return line
    raise ValueError("missing `Phase 9 notes -` line")


def check_docs_readme(path: pathlib.Path) -> tuple[str, list[str]]:
    line = _extract_phase9_notes_line(path.read_text(encoding="utf-8"))
    missing = [marker for marker in REQUIRED_MARKERS if marker not in line]
    return line, missing


def _write(path: pathlib.Path, line: str) -> None:
    path.write_text(f"{line}\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase9-docs-readme-") as tmp:
        tmpdir = pathlib.Path(tmp)
        good = tmpdir / "good.md"
        bad = tmpdir / "bad.md"

        _write(good, "Phase 9 notes - " + " - ".join(REQUIRED_MARKERS))
        _write(
            bad,
            "Phase 9 notes - "
            + " - ".join(
                marker
                for marker in REQUIRED_MARKERS
                if marker
                != "scripts/zigux/check-phase9-trace-events-runtime-packet.py"
            ),
        )

        _, good_missing = check_docs_readme(good)
        _, bad_missing = check_docs_readme(bad)

        if good_missing:
            print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST=fail")
            print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST_REASON=good-case-missed")
            return 1
        if bad_missing != ["scripts/zigux/check-phase9-trace-events-runtime-packet.py"]:
            print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST=fail")
            print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST_REASON=bad-case-did-not-isolate-trace-events-guard")
            return 1

    print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE9_DOCS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=2")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "readme",
        nargs="?",
        type=pathlib.Path,
        default=DEFAULT_README,
        help="path to Documentation/zigux/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        _, missing = check_docs_readme(args.readme)
    except (FileNotFoundError, ValueError) as exc:
        print("PHASE9_DOCS_README_ALIGNMENT=fail")
        print(f"PHASE9_DOCS_README_ALIGNMENT_REASON={exc}")
        return 1

    if missing:
        print("PHASE9_DOCS_README_ALIGNMENT=fail")
        print(
            "PHASE9_DOCS_README_ALIGNMENT_MISSING="
            + ",".join(missing)
        )
        return 1

    print("PHASE9_DOCS_README_ALIGNMENT=pass")
    print(f"PHASE9_DOCS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
