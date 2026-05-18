#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_trace_events_manifest.json"

REQUIRED_FILES = (
    SEQUENCING_PATH,
    MODULE_SLICE_PATH,
    SURVEY_PATH,
    MANIFEST_PATH,
)

SHARED_PACKET_MARKERS = (
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "`zigux/tests/runtime_trace_events_loader_substrate_drift.zig`",
    "`zigux/tests/runtime_trace_events_survey.zig`",
    "`zigux/tests/runtime_trace_events_manifest.json`",
    "`zigux/tests/phase9_build.zig`",
    "`zigux/kernel/runtime_loader.zig`",
)

BLOCKED_BOUNDARY_MARKERS = (
    "runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior",
    "`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication",
)

SEQUENCING_MARKERS = (
    "`Documentation/zigux/phase9-runtime-trace-events-survey.md`",
    "`Documentation/zigux/phase9-runtime-trace-events-module-slice.md`",
    "reviewable family-local starter plus the adjacent shared loader-facing reminder packet",
    "not an absent-loader story",
    *SHARED_PACKET_MARKERS,
    *BLOCKED_BOUNDARY_MARKERS,
)

MODULE_SLICE_MARKERS = (
    "PHASE9_SURVEYED_COMMIT=",
    "`samples/zigux/runtime_trace_events.zig`",
    "`zigux/tests/runtime_trace_events_diff.zig`",
    "the broader runtime-substrate handoff remains a separate blocked step",
    "the live runtime substrate is still missing",
    "The family-local module gate owns the selftest-ready failed-exit rollback path that preserves lifecycle state until registration drain finishes, while still leaving the broader runtime-substrate handoff as a separate blocked step.",
    "The family-local module gate also keeps rejected re-selftest rollback explicit, so invalid repeat selftest attempts leave both the selftest-complete and exited summaries stable while the broader runtime-substrate handoff stays blocked.",
    "rejects non-idle registration state at the metadata-only handoff boundary, and keeps shared release failures from desynchronizing loader state",
    "those alias and depmod surfaces remain review-only metadata boundaries rather than shipped trace-events-family evidence.",
    "Do not invent `validate-phase9.py`, a trace-events-only validator, or a cleared runtime-substrate handoff.",
    "the shared Phase 9 loader-facing packet is also shipped and reviewable",
    "the remaining same-lane work should keep the packet-local notes and manifest aligned with the shipped family-local trace-events proof instead of drifting back to missing-file reminder wording",
    "The next honest follow-through in the same `runtime-pilot` lane is to keep the packet-local survey note, module-slice note, and manifest aligned with the visible family-local trace-events packet, keep the bounded pilot-module contract explicit, and then leave broader follow-up to the separate shared runtime-substrate lanes until a real substrate step lands.",
    *SHARED_PACKET_MARKERS,
    *BLOCKED_BOUNDARY_MARKERS,
)

SURVEY_MARKERS = (
    "PHASE9_SURVEYED_COMMIT=",
    "reviewable family-local starter plus the adjacent shared loader-facing reminder packet",
    "The remaining blocker is the broader Phase 9 runtime substrate.",
    *SHARED_PACKET_MARKERS,
    *BLOCKED_BOUNDARY_MARKERS,
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def parse_manifest(root: Path) -> dict:
    return json.loads(read_text(root, MANIFEST_PATH))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    sequencing = read_text(root, SEQUENCING_PATH)
    module_slice = read_text(root, MODULE_SLICE_PATH)
    survey = read_text(root, SURVEY_PATH)
    manifest = parse_manifest(root)

    surveyed_commit = manifest.get("surveyed_commit", "")
    if not surveyed_commit:
        failures.append("missing_manifest_field:surveyed_commit")
    else:
        expected_marker = f"PHASE9_SURVEYED_COMMIT={surveyed_commit}"
        if expected_marker not in module_slice:
            failures.append(f"missing_marker:{MODULE_SLICE_PATH}:{expected_marker}")
        if expected_marker not in survey:
            failures.append(f"missing_marker:{SURVEY_PATH}:{expected_marker}")

    for marker in SEQUENCING_MARKERS:
        if marker not in sequencing:
            failures.append(f"missing_marker:{SEQUENCING_PATH}:{marker}")
    for marker in MODULE_SLICE_MARKERS:
        if marker not in module_slice:
            failures.append(f"missing_marker:{MODULE_SLICE_PATH}:{marker}")
    for marker in SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"missing_marker:{SURVEY_PATH}:{marker}")

    delivery_paths = {entry.get("path") for entry in manifest.get("delivery_evidence_catalog", []) if isinstance(entry, dict)}
    for marker in (
        "samples/zigux/runtime_trace_events_loader.zig",
        "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
        "zigux/tests/runtime_trace_events_survey.zig",
        "zigux/tests/runtime_trace_events_manifest.json",
        "zigux/tests/phase9_build.zig",
    ):
        if marker not in delivery_paths:
            failures.append(f"missing_delivery_evidence:{marker}")

    ownership_surfaces = {entry.get("surface") for entry in manifest.get("ownership_map", []) if isinstance(entry, dict)}
    for marker in (
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        "zigux/tests/phase9_build.zig",
    ):
        if marker not in ownership_surfaces:
            failures.append(f"missing_ownership_surface:{marker}")

    return failures


def build_fixture(root: Path) -> None:
    manifest = {
        "surveyed_commit": "3c6c7d3fc8e721e8c50e84b512876cee6ad4e015",
        "delivery_evidence_catalog": [
            {"path": "samples/zigux/runtime_trace_events_loader.zig"},
            {"path": "zigux/tests/runtime_trace_events_loader_substrate_drift.zig"},
            {"path": "zigux/tests/runtime_trace_events_survey.zig"},
            {"path": "zigux/tests/runtime_trace_events_manifest.json"},
            {"path": "zigux/tests/phase9_build.zig"},
        ],
        "ownership_map": [
            {"surface": "Documentation/zigux/phase9-runtime-trace-events-survey.md"},
            {"surface": "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"},
            {"surface": "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"},
            {"surface": "zigux/tests/phase9_build.zig"},
        ],
    }
    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Survey",
                "PHASE9_SURVEYED_COMMIT=3c6c7d3fc8e721e8c50e84b512876cee6ad4e015",
                "reviewable family-local starter plus the adjacent shared loader-facing reminder packet",
                "The remaining blocker is the broader Phase 9 runtime substrate.",
                *SHARED_PACKET_MARKERS,
                *BLOCKED_BOUNDARY_MARKERS,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / SEQUENCING_PATH).write_text(
        "\n".join(["# Sequencing", *SEQUENCING_MARKERS]) + "\n",
        encoding="utf-8",
    )
    (root / MODULE_SLICE_PATH).write_text(
        "\n".join(["# Module Slice", "PHASE9_SURVEYED_COMMIT=3c6c7d3fc8e721e8c50e84b512876cee6ad4e015", *MODULE_SLICE_MARKERS]) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="phase9-trace-events-packet-"))
    try:
        build_fixture(temp_root)
        failures = validate(temp_root)
        if failures:
            for failure in failures:
                print(failure)
            return 1
        print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET=pass")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(SEQUENCING_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_MODULE_SLICE_MARKER_COUNT={len(MODULE_SLICE_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
