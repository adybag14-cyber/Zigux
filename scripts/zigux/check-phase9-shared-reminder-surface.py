#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` stay repo-reality gaps on the trusted contents path",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references and `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence",
]

LANE_SEQUENCING_MARKERS = [
    "Trusted mixed rereads on 2026-05-20 confirm three distinct current-master Phase 9 packets.",
    "direct shared-reminder proof is no longer split: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` all keep the allocator/init-flow packet explicit again instead of leaving the scripts-root reminder behind",
    "`zigux/tests/phase9_build.zig` currently exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-bitmap-top-bit-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`",
    "public-tree fallback rereads still return the four loader scaffolds `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_trace_events_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`",
    "current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow packet; the bitmap-side gaps should not be used to deny the allocator/init-flow packet that has already returned through the shared loader surfaces",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
]

SAMPLES_README_MARKERS = [
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` still remain absent on the same trusted path",
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: REVIEW_CHECKLIST_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_MARKERS,
}


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


def find_phase9_routes(makefile_text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in makefile_text.splitlines():
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

    for route in find_phase9_routes(read_text(root, MAKEFILE_PATH)):
        failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == MAKEFILE_PATH:
        return """PYTHON ?= python3
ZIG ?= zig

.PHONY: phase8 phase10 phase12

phase8:
\t@true

phase10:
\t@true

phase12:
\t@true
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
    base = Path(tempfile.mkdtemp(prefix="phase9-shared-reminder-surface-"))
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

        for route in ["phase9", "phase9-test", "phase9-review-checklist"]:
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

    print("PHASE9_SHARED_REMINDER_SURFACE_SELF_TEST=pass")
    print(f"PHASE9_SHARED_REMINDER_SURFACE_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE9_SHARED_REMINDER_SURFACE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_MARKERS)}")
    print(f"PHASE9_SHARED_REMINDER_SURFACE_SAMPLES_MARKER_COUNT={len(SAMPLES_README_MARKERS)}")
    print("PHASE9_SHARED_REMINDER_SURFACE_FORBIDDEN_ROUTE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 shared reminder packet keeps the returned "
            "allocator/init-flow evidence, the partial runtime bitmap reminder, the "
            "review-checklist release-discipline boundaries, and the no-Phase-9-make-route "
            "posture explicit across the checklist, lane-sequencing note, samples README, "
            "and live Makefile."
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
            print(f"PHASE9_SHARED_REMINDER_SURFACE_ERROR={failure}")
        return 1

    print(f"PHASE9_SHARED_REMINDER_SURFACE_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE9_SHARED_REMINDER_SURFACE_SEQUENCING_MARKER_COUNT={len(LANE_SEQUENCING_MARKERS)}")
    print(f"PHASE9_SHARED_REMINDER_SURFACE_SAMPLES_MARKER_COUNT={len(SAMPLES_README_MARKERS)}")
    print("PHASE9_SHARED_REMINDER_SURFACE_FORBIDDEN_ROUTE_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
