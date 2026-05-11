#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import tempfile


REQUIRED_FILES = (
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
    "Documentation/zigux/freeze-map.md",
    "zigux/kernel/runtime_loader.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/phase9_build.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE9_SLICE=shared-runtime-loader-substrate-plan",
    "Documentation/zigux/freeze-map.md",
    "kernel/workqueue.c",
    "Study / Boundary Only",
    "kernel/trace/ring_buffer.c",
    "samples/zigux/runtime_trace_events.zig",
    "runtime-trace-events-substrate-handoff",
    "python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test",
    "python3 scripts/zigux/check-phase9-loader-substrate-plan.py",
    "zig test zigux/tests/runtime_loader_gap_survey.zig",
    "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
    "a working runtime module loader",
    "module_init",
    "module_exit",
    "tracepoint registration parity",
)

REQUIRED_FREEZE_MAP_MARKERS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "Study / Boundary Only",
)

REQUIRED_RUNTIME_LOADER_MARKERS = (
    "command_name",
    "requires_runtime_substrate",
    "provides_selftest_hook",
    "allocator_handoff",
)

REQUIRED_TRACE_EVENTS_LOADER_MARKERS = (
    "tracepoint_probe_register",
    "tracepoint_probe_unregister",
    "waiting_on_runtime_substrate",
    "released_without_substrate",
    "registration_depth",
)

REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS = (
    "runtime-trace-events-substrate-handoff",
    "samples/zigux/runtime_trace_events_loader.zig",
    "kernel/trace/ring_buffer.c",
)

REQUIRED_PHASE9_BUILD_MARKERS = (
    "runtime_trace_events_survey.zig",
    "phase9-runtime-trace-events-loader-tests",
)

REQUIRED_SAMPLE_MARKERS = {
    "samples/zigux/runtime_atomic64_loader.zig": ("requires_runtime_substrate", "released_without_substrate"),
    "samples/zigux/runtime_bitmap_loader.zig": ("requires_runtime_substrate", "released_without_substrate"),
    "samples/zigux/runtime_kretprobe_loader.zig": ("register_kretprobe", "unregister_kretprobe"),
}


def read_text(root: pathlib.Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: pathlib.Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def require_markers(text: str, markers: tuple[str, ...], label: str) -> list[str]:
    return [f"{label}: missing marker `{marker}`" for marker in markers if marker not in text]


def validate(root: pathlib.Path) -> list[str]:
    errors = collect_missing_files(root)
    if errors:
        return [f"missing required file `{rel_path}`" for rel_path in errors]

    note = read_text(root, "Documentation/zigux/phase9-runtime-loader-substrate-plan.md")
    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    runtime_loader = read_text(root, "zigux/kernel/runtime_loader.zig")
    trace_events_loader = read_text(root, "samples/zigux/runtime_trace_events_loader.zig")
    trace_events_manifest = read_text(root, "zigux/tests/runtime_trace_events_manifest.json")
    phase9_build = read_text(root, "zigux/tests/phase9_build.zig")

    errors = []
    errors.extend(require_markers(note, REQUIRED_NOTE_MARKERS, "phase9-runtime-loader-substrate-plan.md"))
    errors.extend(require_markers(freeze_map, REQUIRED_FREEZE_MAP_MARKERS, "freeze-map.md"))
    errors.extend(require_markers(runtime_loader, REQUIRED_RUNTIME_LOADER_MARKERS, "runtime_loader.zig"))
    errors.extend(
        require_markers(
            trace_events_loader,
            REQUIRED_TRACE_EVENTS_LOADER_MARKERS,
            "runtime_trace_events_loader.zig",
        )
    )
    errors.extend(
        require_markers(
            trace_events_manifest,
            REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS,
            "runtime_trace_events_manifest.json",
        )
    )
    errors.extend(require_markers(phase9_build, REQUIRED_PHASE9_BUILD_MARKERS, "phase9_build.zig"))

    for rel_path, markers in REQUIRED_SAMPLE_MARKERS.items():
        errors.extend(require_markers(read_text(root, rel_path), markers, rel_path))

    return errors


def build_fixture(root: pathlib.Path) -> None:
    files = {
        "Documentation/zigux/phase9-runtime-loader-substrate-plan.md": """# Phase 9 Shared Runtime Loader Substrate Plan
PHASE9_SLICE=shared-runtime-loader-substrate-plan
Documentation/zigux/freeze-map.md
kernel/workqueue.c
Study / Boundary Only
kernel/trace/ring_buffer.c
samples/zigux/runtime_trace_events.zig
runtime-trace-events-substrate-handoff
python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test
python3 scripts/zigux/check-phase9-loader-substrate-plan.py
zig test zigux/tests/runtime_loader_gap_survey.zig
zig build test --build-file zigux/tests/phase9_build.zig --summary all
a working runtime module loader
module_init
module_exit
tracepoint registration parity
""",
        "Documentation/zigux/freeze-map.md": "kernel/workqueue.c\nkernel/trace/ring_buffer.c\nStudy / Boundary Only\n",
        "zigux/kernel/runtime_loader.zig": "command_name requires_runtime_substrate provides_selftest_hook allocator_handoff\n",
        "zigux/tests/runtime_trace_events_manifest.json": "runtime-trace-events-substrate-handoff samples/zigux/runtime_trace_events_loader.zig kernel/trace/ring_buffer.c\n",
        "zigux/tests/phase9_build.zig": "runtime_trace_events_survey.zig phase9-runtime-trace-events-loader-tests\n",
        "samples/zigux/runtime_atomic64_loader.zig": "requires_runtime_substrate released_without_substrate\n",
        "samples/zigux/runtime_bitmap_loader.zig": "requires_runtime_substrate released_without_substrate\n",
        "samples/zigux/runtime_kretprobe_loader.zig": "register_kretprobe unregister_kretprobe\n",
        "samples/zigux/runtime_trace_events_loader.zig": "tracepoint_probe_register tracepoint_probe_unregister waiting_on_runtime_substrate released_without_substrate registration_depth\n",
    }

    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = pathlib.Path(tmp_dir)
        build_fixture(root)
        errors = validate(root)
        if errors:
            raise AssertionError(f"expected passing fixture, got {errors}")

        broken_note = root / "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
        broken_note.write_text("PHASE9_SLICE=shared-runtime-loader-substrate-plan\n", encoding="utf-8")
        errors = validate(root)
        if not any("kernel/workqueue.c" in error for error in errors):
            raise AssertionError(f"expected missing workqueue marker error, got {errors}")

    print("PHASE9_LOADER_SUBSTRATE_PLAN_SELF_TEST=pass")
    return 0


def default_repo_root() -> pathlib.Path:
    root = pathlib.Path(__file__).resolve().parent
    if root.name == "zigux" and root.parent.name == "scripts":
        return root.parent.parent
    return root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Phase 9 shared runtime-loader substrate plan markers.",
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=default_repo_root(),
        help="repository root to inspect (default: repository root when run from scripts/zigux)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    errors = validate(args.repo_root)
    if errors:
        for error in errors:
            print(f"PHASE9_LOADER_SUBSTRATE_PLAN_ERROR={error}")
        return 1

    print(f"PHASE9_LOADER_SUBSTRATE_PLAN_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE9_LOADER_SUBSTRATE_PLAN_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_NOTE_MARKERS) + len(REQUIRED_FREEZE_MAP_MARKERS) + len(REQUIRED_RUNTIME_LOADER_MARKERS) + len(REQUIRED_TRACE_EVENTS_LOADER_MARKERS) + len(REQUIRED_TRACE_EVENTS_MANIFEST_MARKERS) + len(REQUIRED_PHASE9_BUILD_MARKERS) + sum(len(markers) for markers in REQUIRED_SAMPLE_MARKERS.values())}"
    )
    print("PHASE9_LOADER_SUBSTRATE_PLAN=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
