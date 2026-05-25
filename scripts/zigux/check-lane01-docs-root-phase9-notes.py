#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_README = Path("Documentation/zigux/README.md")

PHASE6_HEADING = "Phase 6 notes -"
PHASE9_HEADING = "Phase 9 notes -"
PHASE12_HEADING = "Phase 12 notes -"

REQUIRED_MARKERS = (
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
    "keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.",
    "* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    "* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.",
    "* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned.",
)

CURRENT_LIKE_README = """# Zigux Documentation
Phase 6 notes - placeholder
Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.
* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.
* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.
* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.
* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.
* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned.
Phase 12 notes - placeholder
"""


def collect_failures(root: Path) -> list[str]:
    text = (root / DOCS_ROOT_README).read_text(encoding="utf-8")

    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing:{marker}")

    if text.count(PHASE9_HEADING) != 1:
        failures.append("count:Phase 9 notes")

    phase6_at = text.find(PHASE6_HEADING)
    phase9_at = text.find(PHASE9_HEADING)
    phase12_at = text.find(PHASE12_HEADING)
    if -1 in (phase6_at, phase9_at, phase12_at):
        if phase6_at == -1:
            failures.append(f"missing:{PHASE6_HEADING}")
        if phase9_at == -1:
            failures.append(f"missing:{PHASE9_HEADING}")
        if phase12_at == -1:
            failures.append(f"missing:{PHASE12_HEADING}")
    elif not (phase6_at < phase9_at < phase12_at):
        failures.append("order:Phase6->Phase9->Phase12")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    _write(root / DOCS_ROOT_README, CURRENT_LIKE_README)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_docs_root_phase9_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (
                "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.\n",
                [
                    "missing:Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
                    "missing:keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
                    "count:Phase 9 notes",
                    "missing:Phase 9 notes -",
                ],
            ),
            (
                "* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.\n",
                [
                    "missing:* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes."
                ],
            ),
            (
                "* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.\n",
                [
                    "missing:* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only."
                ],
            ),
            (
                "* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.\n",
                [
                    "missing:* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved."
                ],
            ),
            (
                "* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.\n",
                [
                    "missing:* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete."
                ],
            ),
            (
                "* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned.\n",
                [
                    "missing:* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned."
                ],
            ),
        )

        for needle, expected in cases:
            _write(root / DOCS_ROOT_README, CURRENT_LIKE_README.replace(needle, "", 1))
            failures = collect_failures(root)
            if failures != expected:
                raise AssertionError(f"unexpected failures for {needle!r}: {failures}")
            _write(root / DOCS_ROOT_README, CURRENT_LIKE_README)
            case_count += 1

        reordered = CURRENT_LIKE_README.replace(
            "Phase 6 notes - placeholder\n",
            "",
            1,
        ).replace(
            "Phase 12 notes - placeholder\n",
            "Phase 6 notes - placeholder\nPhase 12 notes - placeholder\n",
            1,
        )
        _write(root / DOCS_ROOT_README, reordered)
        failures = collect_failures(root)
        if failures != ["order:Phase6->Phase9->Phase12"]:
            raise AssertionError(f"unexpected ordering failures: {failures}")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE9_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE9_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the live Zigux docs root keeps its Phase 9 notes packet."
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
        help="exercise the checker against synthetic docs-root fixtures",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like repository root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE9_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE9_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE9_NOTES_SECTION_ORDER=Phase6->Phase9->Phase12")
    print("LANE01_DOCS_ROOT_PHASE9_NOTES_LINKED_PATH_COUNT=11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
