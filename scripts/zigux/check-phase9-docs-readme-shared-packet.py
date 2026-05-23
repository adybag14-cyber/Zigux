#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

DOCS_README_PATH = "Documentation/zigux/README.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / DOCS_README_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_REQUIRED_MARKERS = [
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/runtime_bitmap_manifest.json` are the current trusted bitmap-side evidence surfaces, while `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` stay repo-reality gaps on the same trusted path.",
]

FREEZE_MAP_REQUIRED_MARKERS = [
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`scripts/zigux/README.md`",
    "`samples/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
]

STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS = [
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "this note is an inventory and handoff surface, not an approval record",
    "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "The shared Phase 9 reminder family should now be read as three distinct truths:",
    "the trace-events runtime packet is still the shipped direct current-`master` proof",
    "the returned shared runtime-loader allocator/init-flow and command/environment boundary packet stay neighboring shared-owner evidence",
    "the bitmap side now keeps a broader direct packet on trusted rereads",
    "a fresh 2026-05-22 reread also showed that `Documentation/zigux/README.md` now undercounts the shared Phase 9 packet by omitting `scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
]

SAMPLES_README_REQUIRED_MARKERS = [
    "The surviving direct runtime-module sample packet in this directory is still centered on `samples/zigux/runtime_trace_events.zig`.",
    "Fresh trusted mixed reread on 2026-05-22 also confirms a broader runtime bitmap sample-side packet on current `master`",
]

TESTS_README_REQUIRED_MARKERS = [
    "Keep the partial runtime bitmap reminder packet distinct from that returned shared loader packet",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        DOCS_README_PATH,
        FREEZE_MAP_PATH,
        STUDY_ONLY_ACCOUNTING_PATH,
        LANE_SEQUENCING_PATH,
        SCRIPTS_README_PATH,
        SAMPLES_README_PATH,
        TESTS_README_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in {
        DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
        FREEZE_MAP_PATH: FREEZE_MAP_REQUIRED_MARKERS,
        STUDY_ONLY_ACCOUNTING_PATH: STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS,
        LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
        SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
        SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
        TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
    }.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    marker_map = {
        DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
        FREEZE_MAP_PATH: FREEZE_MAP_REQUIRED_MARKERS,
        STUDY_ONLY_ACCOUNTING_PATH: STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS,
        LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
        SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
        SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
        TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
    }
    prefix = {
        DOCS_README_PATH: "# Zigux Documentation\n\n",
        FREEZE_MAP_PATH: "# Zigux Freeze Map\n\n",
        STUDY_ONLY_ACCOUNTING_PATH: "# Phase 15 Study-Only Anchor Accounting\n\n",
        LANE_SEQUENCING_PATH: "# Phase 9 Runtime Pilot Lane Sequencing\n\n",
        SCRIPTS_README_PATH: "# scripts/zigux\n\n",
        SAMPLES_README_PATH: "# samples/zigux\n\n",
        TESTS_README_PATH: "# zigux/tests\n\n",
    }[rel_path]
    bulletized = []
    for marker in marker_map[rel_path]:
        bulletized.append(f"- {marker}")
    return prefix + "\n".join(bulletized) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in [
        DOCS_README_PATH,
        FREEZE_MAP_PATH,
        STUDY_ONLY_ACCOUNTING_PATH,
        LANE_SEQUENCING_PATH,
        SCRIPTS_README_PATH,
        SAMPLES_README_PATH,
        TESTS_README_PATH,
    ]:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-docs-readme-shared-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in {
            DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
            FREEZE_MAP_PATH: FREEZE_MAP_REQUIRED_MARKERS,
            STUDY_ONLY_ACCOUNTING_PATH: STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS,
            LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
            SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
            SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
            TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
        }.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                if current.count(marker) != 1:
                    continue
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [
            DOCS_README_PATH,
            FREEZE_MAP_PATH,
            STUDY_ONLY_ACCOUNTING_PATH,
            LANE_SEQUENCING_PATH,
            SCRIPTS_README_PATH,
            SAMPLES_README_PATH,
            TESTS_README_PATH,
        ]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_DOCS_README_SHARED_PACKET_SELF_TEST=pass")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_STUDY_ONLY_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_LANE_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current docs-root Phase 9 shared reminder packet stays aligned "
            "with the freeze-map route-back wording, the study-only anchor accounting note, "
            "the phase9 lane sequencing note, and the neighboring scripts, samples, and tests reminders."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_DOCS_README_SHARED_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_DOCS_README_SHARED_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_STUDY_ONLY_MARKER_COUNT={len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}")
    print(f"PHASE9_DOCS_README_SHARED_PACKET_LANE_MARKER_COUNT={len(LANE_SEQUENCING_REQUIRED_MARKERS)}")
    print("PHASE9_DOCS_README_SHARED_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
