#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-bitmap-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
SURVEY_GATE_PATH = "zigux/tests/runtime_bitmap_survey.zig"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
MAKEFILE_PATH = "zigux/Makefile"

PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

CHECKLIST_REQUIRED_MARKERS = [
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` stay repo-reality gaps on the trusted contents path",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "### 3. The runtime bitmap side is still only partial",
    "direct authenticated reads do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    "the same trusted read path still returns missing for `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`",
    "the bitmap-side gaps should not be used to deny the allocator/init-flow packet that has already returned through the shared loader surfaces",
    "the partial runtime bitmap reminder packet explicit without overstating what has actually returned",
]

SURVEY_NOTE_REQUIRED_MARKERS = [
    "`PHASE9_STATUS=active`",
    "`PHASE9_LANE_KEY=P9-L08`",
    "`PHASE9_SURVEYED_COMMIT=2026-05-20-runtime-bitmap-partial-return`",
    "trusted current-tree contents reads on 2026-05-20 do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    "the same trusted read path still returns missing for `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`",
    "keep `zigux/tests/phase9_build.zig` explicit only as a bounded Phase 9 build bundle whose live body now reruns the restored direct sample, survey, and top-bit proofs",
    "`partial_packet_without_loadable_runtime_substrate`",
]

MODULE_SLICE_REQUIRED_MARKERS = [
    "`PHASE9_SLICE=runtime-bitmap-partial-slice`",
    "## Current visible slice",
    "## Repo-reality gaps inside the bitmap family",
    "The shared `zigux/tests/phase9_build.zig` bundle now reruns only the direct sample, survey gate, and top-bit companion and still does not prove that the broader runtime bitmap loader packet returned.",
    "The shared runtime substrate is still absent, and the loader, module, diff, and manifest legs are still absent on the trusted read path",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "keep the separate runtime bitmap family parked as adjacent Phase 9 support material through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`; direct authenticated contents rereads now materialize that restored sample-plus-top-bit packet while still returning missing for `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`, so keep the bitmap-side packet framed as partial reminder evidence rather than proof that the deeper bitmap loader packet returned or as a fifth Phase 5 sample",
    "keep `zigux/tests/phase9_build.zig` explicit as the returned `phase9-runtime-atomic64-diff` build shard plus the bounded bitmap-family rerun handles rather than proof that every deeper runtime-publication surface has returned",
    "keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes",
]

SAMPLES_README_REQUIRED_MARKERS = [
    "Fresh trusted mixed reread on 2026-05-20 also restored a narrower runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` still remain absent on the same trusted path.",
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
]

SURVEY_GATE_REQUIRED_MARKERS = [
    'const present_bitmap_family_files = [_][]const u8{',
    '"Documentation/zigux/phase9-runtime-bitmap-survey.md"',
    '"Documentation/zigux/phase9-runtime-bitmap-module-slice.md"',
    '"zigux/tests/runtime_bitmap_survey.zig"',
    '"zigux/tests/phase9_build.zig"',
    '"samples/zigux/runtime_bitmap.zig"',
    '"samples/zigux/runtime_bitmap_top_bit_contract.zig"',
    'const missing_bitmap_family_files = [_][]const u8{',
    '"samples/zigux/runtime_bitmap_loader.zig"',
    '"zigux/tests/runtime_bitmap_module.zig"',
    '"zigux/tests/runtime_bitmap_diff.zig"',
    '"zigux/tests/runtime_bitmap_manifest.json"',
    'test "phase9 runtime bitmap survey gate matches the partial bitmap reminder packet" {',
]

PHASE9_BUILD_REQUIRED_MARKERS = [
    '"phase9-runtime-bitmap-sample-tests"',
    '"phase9-runtime-bitmap-survey-tests"',
    '"phase9-runtime-bitmap-top-bit-tests"',
    '"Run the Phase 9 runtime bitmap sample, survey, and top-bit tests."',
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: CHECKLIST_REQUIRED_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
    SURVEY_NOTE_PATH: SURVEY_NOTE_REQUIRED_MARKERS,
    MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
    SURVEY_GATE_PATH: SURVEY_GATE_REQUIRED_MARKERS,
    PHASE9_BUILD_PATH: PHASE9_BUILD_REQUIRED_MARKERS,
}

MAKEFILE_FORBIDDEN_ROUTE_FIXTURES = ["phase9", "phase9-test", "phase9-runtime-bitmap-tests"]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / REVIEW_CHECKLIST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def find_makefile_phase9_routes(text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(".PHONY:"):
            continue
        if stripped.startswith("phase9") and ":" in stripped:
            routes.append(stripped.split(":", 1)[0])
    return routes


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    for route in find_makefile_phase9_routes(makefile):
        failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == MAKEFILE_PATH:
        return """PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := ..

.PHONY: phase8-test phase10-test phase12-test

phase8-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase10-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase12-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all
"""
    return "# fixture\n\n" + "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-bitmap-reminder-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for route in MAKEFILE_FORBIDDEN_ROUTE_FIXTURES:
            seed_fixture_tree(base)
            current = read_text(base, MAKEFILE_PATH)
            write_text(base / MAKEFILE_PATH, current + f"\n{route}:\n\t@true\n")
            expect_failure(base, f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

        for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SURVEY_NOTE_MARKER_COUNT={len(SURVEY_NOTE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SURVEY_GATE_MARKER_COUNT={len(SURVEY_GATE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_PHASE9_BUILD_MARKER_COUNT={len(PHASE9_BUILD_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 shared reminder surfaces keep the partial runtime bitmap packet, "
            "its trusted-path repo-reality gaps, the bounded phase9_build rerun handles, and the no-Phase-9-make-route boundary explicit."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_LANE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SURVEY_NOTE_MARKER_COUNT={len(SURVEY_NOTE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SAMPLES_README_MARKER_COUNT={len(SAMPLES_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SURVEY_GATE_MARKER_COUNT={len(SURVEY_GATE_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_PHASE9_BUILD_MARKER_COUNT={len(PHASE9_BUILD_REQUIRED_MARKERS)}")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FORBIDDEN_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_FORBIDDEN_ROUTE_FIXTURES)}")
    print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
