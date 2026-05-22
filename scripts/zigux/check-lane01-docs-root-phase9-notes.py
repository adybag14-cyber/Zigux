#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_README = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 9 notes - `Documentation/zigux/freeze-map.md`",
    "keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
    "* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    "* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the partial bitmap packet, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, and the first-loadable parity-survey handle, but it is not proof that the blocked publication boundaries or the full bitmap family returned.",
)

ORDER_MARKERS = (
    "Phase 6 notes",
    "Phase 9 notes",
    "Phase 12 notes",
)


def collect_failures(root: Path) -> list[str]:
    text = (root / DOCS_ROOT_README).read_text(encoding="utf-8")

    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing:{marker}")

    if text.count("Phase 9 notes") != 1:
        failures.append("count:Phase 9 notes")

    positions = [text.find(marker) for marker in ORDER_MARKERS]
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        failures.append("order:Phase 6 notes -> Phase 9 notes -> Phase 12 notes")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation
Phase 6 notes - placeholder
Phase 9 notes - `Documentation/zigux/freeze-map.md`
keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.
* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.
* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.
* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.
* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the partial bitmap packet, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, and the first-loadable parity-survey handle, but it is not proof that the blocked publication boundaries or the full bitmap family returned.
Phase 12 notes - placeholder
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_docs_root_phase9_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_ROOT_README, _sample_readme())

        if collect_failures(root):
            raise AssertionError("baseline phase9 fixture should pass")
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Phase 9 notes - `Documentation/zigux/freeze-map.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:Phase 9 notes - `Documentation/zigux/freeze-map.md`",
            "count:Phase 9 notes",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected phase9 heading failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected phase9 summary failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected parked-packet failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-boundary failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected trace-events failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected runtime-loader failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the partial bitmap packet, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, and the first-loadable parity-survey handle, but it is not proof that the blocked publication boundaries or the full bitmap family returned.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the partial bitmap packet, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, and the first-loadable parity-survey handle, but it is not proof that the blocked publication boundaries or the full bitmap family returned."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected build-bundle failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            """# Zigux Documentation
Phase 9 notes - `Documentation/zigux/freeze-map.md`
keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.
* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.
* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.
* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.
* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the partial bitmap packet, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, and the first-loadable parity-survey handle, but it is not proof that the blocked publication boundaries or the full bitmap family returned.
Phase 6 notes - placeholder
Phase 12 notes - placeholder
""",
        )
        failures = collect_failures(root)
        expected = ["order:Phase 6 notes -> Phase 9 notes -> Phase 12 notes"]
        if failures != expected:
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
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("LANE01_DOCS_ROOT_PHASE9_NOTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
