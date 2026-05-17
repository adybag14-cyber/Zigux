#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "samples/zigux/README.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
SAMPLES_README_PATH = "samples/zigux/README.md"

SECTION_MARKER = "## Separate Phase 9 runtime pilot family"
SEQUENCING_MARKER = "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
CHECKLIST_MARKER = "`Documentation/zigux/review-checklist.md`"
BOUNDARY_CHECKER_MARKER = "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
TESTS_README_MARKER = "`zigux/tests/README.md`"
TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
BACKLOG_MARKER = "current `master` does not currently expose the broader shared runtime-loader packet"
PHASE2_BOUNDARY_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "`rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence"
BITMAP_PHASE5_BOUNDARY_MARKER = "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample"

REQUIRED_MARKERS = [
    SECTION_MARKER,
    SEQUENCING_MARKER,
    CHECKLIST_MARKER,
    BOUNDARY_CHECKER_MARKER,
    TESTS_README_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    BACKLOG_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
    BITMAP_PHASE5_BOUNDARY_MARKER,
]

FORBIDDEN_MARKERS = [
    "`samples/zigux/runtime_bitmap.zig`",
    "`samples/zigux/runtime_bitmap_loader.zig`",
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    "phase9-runtime-bitmap-top-bit-tests",
    "make -C zigux phase9-runtime-bitmap-top-bit-test",
    "make -C zigux phase9-runtime-loader-shared-tests",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    samples_readme_path = root / SAMPLES_README_PATH
    if not samples_readme_path.exists():
        return [f"missing_file:{SAMPLES_README_PATH}"]

    text = read_text(root, SAMPLES_README_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{SAMPLES_README_PATH}:{marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden_marker:{SAMPLES_README_PATH}:{marker}")
    return failures


def build_fixture_text() -> str:
    return f'''# samples/zigux

{SECTION_MARKER}
Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.

* keep {SEQUENCING_MARKER}, {CHECKLIST_MARKER}, {BOUNDARY_CHECKER_MARKER}, and {TESTS_README_MARKER} aligned with the surviving direct runtime-module sample {TRACE_EVENTS_SAMPLE_MARKER}
* keep the current direct runtime-module evidence explicit: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}
* keep saying clearly that {BACKLOG_MARKER}, so `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds stay backlog references unless a fresh repo reread proves they have returned
* keep older cross-phase non-owner boundaries explicit: {PHASE2_BOUNDARY_MARKER}, while {PHASE3_BOUNDARY_MARKER}
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, keep it in the separate runtime lane instead of widening Phase 5
{BITMAP_PHASE5_BOUNDARY_MARKER}. Keep direct bitmap helper reviewability in its existing helper or runtime lanes instead of counting runtime-facing bitmap work as a fifth approved Phase 5 sample idiom.
'''


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-samples-readme-runtime-packet-"))
    try:
        readme_path = base / SAMPLES_README_PATH
        fixture = build_fixture_text()
        write_text(readme_path, fixture)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            write_text(readme_path, fixture.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SAMPLES_README_PATH}:{marker}")
            write_text(readme_path, fixture)

        for marker in FORBIDDEN_MARKERS:
            write_text(readme_path, fixture + "\n" + marker + "\n")
            expect_failure(base, f"forbidden_marker:{SAMPLES_README_PATH}:{marker}")
            write_text(readme_path, fixture)

        readme_path.unlink()
        expect_failure(base, f"missing_file:{SAMPLES_README_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_SAMPLES_README_RUNTIME_PACKET_SELF_TEST=pass")
    print(f"PHASE9_SAMPLES_README_RUNTIME_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_RUNTIME_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 9 sample-root reminder stays aligned with the surviving trace-events runtime packet and does not drift back toward removed runtime-loader or runtime-bitmap packet claims."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_SAMPLES_README_RUNTIME_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_SAMPLES_README_RUNTIME_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE9_SAMPLES_README_RUNTIME_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    print("PHASE9_SAMPLES_README_RUNTIME_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())