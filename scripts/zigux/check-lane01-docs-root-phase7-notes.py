#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")
SECTION_HEADING = "Phase 7 notes -"
NEXT_HEADING = "Phase 9 notes -"
REQUIRED_MARKERS = (
    "`Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
    "`scripts/zigux/check-phase7-shared-surface.py`",
    "`scripts/zigux/check-phase7-build-wiring.py`",
    "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
    "`scripts/zigux/check-phase7-argv-split-packet.py`",
    "`scripts/zigux/validate-phase7.py`",
    "`zigux/tests/phase7_leaf_library_evidence_manifest.json`",
    "`zigux/tests/phase7_build.zig`",
    "`zigux/Makefile`",
    "`lib/string_helpers.zig`",
    "`lib/cmdline.zig`",
    "`lib/argv_split.zig`",
    "`lib/rbtree.zig`",
    "`make -C zigux phase7-validate`",
    "workflow recovery claims, or deeper runtime-family validation routes.",
)
EXPECTED_SECTION_LINES = 5


def extract_phase7_section(root: Path) -> tuple[str, ...]:
    readme_lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()

    start = next((idx for idx, line in enumerate(readme_lines) if line.startswith(SECTION_HEADING)), None)
    if start is None:
        raise AssertionError(f"missing heading: {SECTION_HEADING}")

    end = next((idx for idx in range(start + 1, len(readme_lines)) if readme_lines[idx].startswith(NEXT_HEADING)), None)
    if end is None:
        raise AssertionError(f"missing heading: {NEXT_HEADING}")

    section = tuple(line for line in readme_lines[start:end] if line.strip())
    if len(section) != EXPECTED_SECTION_LINES:
        raise AssertionError(
            f"unexpected section line count: expected {EXPECTED_SECTION_LINES}, found {len(section)}"
        )
    return section


def check_phase7_notes(root: Path) -> list[str]:
    try:
        section = extract_phase7_section(root)
    except AssertionError as exc:
        return [str(exc)]

    section_text = "\n".join(section)
    missing = [marker for marker in REQUIRED_MARKERS if marker not in section_text]
    if missing:
        return [f"missing marker: {marker}" for marker in missing]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation
Phase 6 notes - prior packet boundary
Phase 7 notes - `Documentation/zigux/phase7-leaf-library-evidence-catalog.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase7-shared-surface.py` - `scripts/zigux/check-phase7-build-wiring.py` - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py` - `scripts/zigux/check-phase7-argv-split-packet.py` - `scripts/zigux/validate-phase7.py` - `zigux/tests/phase7_leaf_library_evidence_manifest.json` - `zigux/tests/phase7_build.zig` - `zigux/Makefile` - `lib/string_helpers.zig` - `lib/cmdline.zig` - `lib/argv_split.zig` - `lib/rbtree.zig` keep the bounded Phase 7 docs-root packet explicit through the returned leaf-library evidence catalog, the shared scripts-root and tests-root reminders, the shipped shared-surface, build-wiring, make-wrapper self-test alignment, and dedicated `argv_split` guards, the validator entrypoint, the shared machine-readable manifest, the shared build graph, the narrow `phase7-validate` wrapper foothold, and the four roadmap-backed helper anchors instead of letting the docs root skip the first reusable runtime helper family now live on current `master`.
* the current docs-root Phase 7 reminder packet should stay parked on `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase7-shared-surface.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` so the docs root matches the same shared leaf-library evidence packet already described by the evidence catalog, the scripts-root reminder, the tests-root reminder, the manifest-backed inventory, the shared build graph, and the narrow Makefile foothold.
* current `master` directly serves the four roadmap-backed helper anchors through `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig`, so keep the docs-root reminder reviewable through that returned helper packet instead of restating helper-local semantics here.
* `zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, and sample-boundary routes plus the shared `test` step, while `zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet.
* `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 reminder packet without widening it into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes.
Phase 9 notes - next packet boundary
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase7_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        errors = check_phase7_notes(root)
        if errors:
            raise AssertionError(f"baseline Lane 01 Phase 7 fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Phase 7 notes -", "Phase Seven notes -", 1))
        errors = check_phase7_notes(root)
        if errors != [f"missing heading: {SECTION_HEADING}"]:
            raise AssertionError(f"unexpected heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Phase 9 notes -", "Phase Nine notes -", 1))
        errors = check_phase7_notes(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`scripts/zigux/check-phase7-build-wiring.py`",
                "`scripts/zigux/check-phase7-build-map.py`",
            ),
        )
        errors = check_phase7_notes(root)
        expected = ["missing marker: `scripts/zigux/check-phase7-build-wiring.py`"]
        if errors != expected:
            raise AssertionError(f"unexpected build-wiring error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("`lib/rbtree.zig`", "`lib/redblack_tree.zig`"),
        )
        errors = check_phase7_notes(root)
        expected = ["missing marker: `lib/rbtree.zig`"]
        if errors != expected:
            raise AssertionError(f"unexpected helper-anchor error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("`make -C zigux phase7-validate`", "`make -C zigux phase7-check`"),
        )
        errors = check_phase7_notes(root)
        expected = ["missing marker: `make -C zigux phase7-validate`"]
        if errors != expected:
            raise AssertionError(f"unexpected wrapper-route error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "* `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 reminder packet without widening it into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes.\n",
                "",
                1,
            ),
        )
        errors = check_phase7_notes(root)
        if errors != [f"unexpected section line count: expected {EXPECTED_SECTION_LINES}, found 4"]:
            raise AssertionError(f"unexpected section-count error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "workflow recovery claims, or deeper runtime-family validation routes.",
                "workflow recovery claims or broader runtime validation routes.",
                1,
            ),
        )
        errors = check_phase7_notes(root)
        expected = ["missing marker: workflow recovery claims, or deeper runtime-family validation routes."]
        if errors != expected:
            raise AssertionError(f"unexpected validation-line error: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE7_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE7_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 7 reminder packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_phase7_notes(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 docs-root Phase 7 notes check passed.")
    print(f"LANE01_DOCS_ROOT_PHASE7_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE7_NOTES_SECTION_ORDER=Phase6->Phase7->Phase9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
