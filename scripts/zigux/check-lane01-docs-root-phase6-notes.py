#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

PHASE5_HEADING = "Phase 5 notes - "
PHASE6_HEADING = "Phase 6 notes - "
PHASE9_HEADING = "Phase 9 notes - "

REQUIRED_MARKERS = (
    "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `zigux/tests/phase6_build.zig` - `zigux/tests/phase6_helper_evidence_manifest.json` - `zigux/tests/phase6_helper_parity_manifest.json` - `scripts/zigux/check-phase6-shared-surface.py` - `scripts/zigux/check-phase6-present-entrypoints.py` - `zigux/Makefile` keep the bounded Phase 6 docs-root packet explicit through the shared helper-evidence and helper-parity catalogs, the current scripts-root and tests-root reminders, the shared build foothold, the shared machine-readable manifests, the present-entrypoint guard, and the returned Makefile wrapper surface instead of leaving the active leaf-helper tranche implicit from neighboring reminder surfaces alone.",
    "* the current docs-root Phase 6 reminder packet should stay parked on `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, and `scripts/zigux/check-phase6-present-entrypoints.py`, and `zigux/Makefile` so the docs root matches the same shared helper-evidence packet already described by the scripts-root reminder, the tests-root reminder, and the two shared manifests.",
    "* current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`, their focused `zigux/tests/phase6_*` helper and perf replays, the restored `zigux/tests/phase6_build.zig` foothold, and the current `zigux/Makefile` wrapper family, so keep the docs-root reminder reviewable through that returned helper-evidence packet instead of restating helper-local semantics here.",
    "* authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep both note surfaces inside the current docs-root evidence packet beside the shared manifests instead of framing the broader perf-note surface as public-tree-backed companion evidence.",
    "* `python3 scripts/zigux/check-phase6-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-perf` replay the bounded current Phase 6 reminder packet without widening it into missing parity companions or helper-local implementation follow-through.",
)


def collect_errors(root: Path) -> list[str]:
    content = (root / DOCS_README_PATH).read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            errors.append(f"missing:{marker}")

    phase5_index = content.find(PHASE5_HEADING)
    phase6_index = content.find(PHASE6_HEADING)
    phase9_index = content.find(PHASE9_HEADING)

    if phase5_index == -1:
        errors.append(f"missing:{PHASE5_HEADING}")
    if phase6_index == -1:
        errors.append(f"missing:{PHASE6_HEADING}")
    if phase9_index == -1:
        errors.append(f"missing:{PHASE9_HEADING}")

    if phase5_index != -1 and phase6_index != -1 and phase5_index >= phase6_index:
        errors.append("order:Phase 5 notes must appear before Phase 6 notes")
    if phase6_index != -1 and phase9_index != -1 and phase6_index >= phase9_index:
        errors.append("order:Phase 6 notes must appear before Phase 9 notes")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return f"""# Zigux Documentation
{PHASE5_HEADING}placeholder
{REQUIRED_MARKERS[0]}
{REQUIRED_MARKERS[1]}
{REQUIRED_MARKERS[2]}
{REQUIRED_MARKERS[3]}
{REQUIRED_MARKERS[4]}
{PHASE9_HEADING}placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase6_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_errors(root):
            raise AssertionError("baseline Phase 6 fixture should pass")
        case_count += 1

        for marker in REQUIRED_MARKERS:
            _write(root / DOCS_README_PATH, _sample_docs_readme().replace(marker + "\n", "", 1))
            errors = collect_errors(root)
            expected = [f"missing:{marker}"]
            if marker.startswith(PHASE6_HEADING):
                expected.append(f"missing:{PHASE6_HEADING}")
            if errors != expected:
                raise AssertionError(f"unexpected errors for marker removal: {errors}")
            case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            f"{PHASE5_HEADING}placeholder\n"
            f"{PHASE9_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS)
            + "\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 6 notes must appear before Phase 9 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 6/9 order case: {errors}")
        case_count += 1

        reordered = (
            "# Zigux Documentation\n"
            + REQUIRED_MARKERS[0]
            + "\n"
            f"{PHASE5_HEADING}placeholder\n"
            + "\n".join(REQUIRED_MARKERS[1:])
            + "\n"
            f"{PHASE9_HEADING}placeholder\n"
        )
        _write(root / DOCS_README_PATH, reordered)
        errors = collect_errors(root)
        expected = ["order:Phase 5 notes must appear before Phase 6 notes"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for Phase 5/6 order case: {errors}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE6_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE6_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current docs-root Phase 6 reminder packet remains aligned."
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
        help="exercise the checker against synthetic Phase 6 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE6_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE6_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE6_NOTES_SECTION_ORDER=Phase5->Phase6->Phase9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
