#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    BOUNDARY_SURVEY_PATH,
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase8.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    MANIFEST_PATH,
    PHASE8_BUILD_PATH,
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/README.md": [
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "while the docs-root summary stays aligned with the live scripts-root and tests-root reminder packet on `master`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared parked Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
        "`zigux/tests/phase8_cpu_mask.zig`",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`zigux/tests/phase8_logging.zig`",
        "`zigux/tests/phase8_pin_path.zig`",
        "`zigux/tests/phase8_bpf_type_names.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "do not let older absent-file assumptions overrule current tree evidence",
        "### 4. Shared wording lane",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback",
        "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
        "`Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
        "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "`Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet",
        "`phase8_cpu_mask.zig`",
        "`phase8_logging.zig`",
        "`phase8_pin_path.zig`",
        "`phase8_bpf_type_names.zig`",
        "`phase8_file_path_handle_bridge.zig`",
        "`phase8_perf_buffer_poll.zig`",
        "`phase8_perf_buffer_poll_only_build.zig`",
        "`phase8_libbpf_segments.zig`",
        "`phase8_libbpf_segments_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`",
        "`make -C zigux phase8-test`",
        "`zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
        "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`",
        "Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.",
        "The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.",
        "The real current gap is now survey truthfulness about the already-landed checker packet, not a missing checker rule or docs-root summary.",
        "Exact 2026-05-13 readback closes the earlier docs-root reopen cue: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py` aligned with the closed docs-root cue",
        "this packet still keeps `standalone timer or clockevent helper behavior` and broader timeout-sensitive routing behavior out of scope",
        "especially the explicit `standalone timer or clockevent helper behavior` and broader timeout-sensitive routing behavior boundaries that keep this packet smaller than the deferred interrupt-routing work.",
        "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        "The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
        "Keep the libbpf survey packet parked after this survey-and-checker sync unless a fresh shared reminder-surface drift reappears against the current readable helper-plus-build evidence.",
    ],
    BOUNDARY_SURVEY_PATH: [
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`",
        "`standalone timer or clockevent helper behavior`",
        "broader timeout-sensitive routing behavior",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "PHASE8_SLICE=libbpf-perf-buffer-poll",
        "make -C zigux phase8-perf-buffer-poll-test",
        "no standalone timer helper behavior",
        "no standalone clockevent helper behavior",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "make -C zigux phase8-validate",
    ],
    "scripts/zigux/validate-phase8.py": [
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "zigux/Makefile",
        "zigux/tests/README.md",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-validate",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ],
    MANIFEST_PATH: [
        '"slug": "fdinfo-map-info-helpers", "status": "starter_landed"',
        '"slug": "map-reuse-compatibility", "status": "starter_landed"',
        '"slug": "perf-buffer-online-cpu-routing", "status": "deferred_high_risk"',
        '"slug": "perf-buffer-poll-bookkeeping", "status": "starter_landed"',
    ],
    PHASE8_BUILD_PATH: [
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),',
        '.root_source_file = b.path("phase8_cpu_mask.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/logging.zig"),',
        '.root_source_file = b.path("phase8_logging.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/pin_path.zig"),',
        '.root_source_file = b.path("phase8_pin_path.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/type_names.zig"),',
        '.root_source_file = b.path("phase8_bpf_type_names.zig"),',
        '.root_source_file = b.path("phase8_libbpf_segments.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),',
        '.root_source_file = b.path("phase8_file_path_handle_bridge.zig"),',
        '.root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),',
        '.root_source_file = b.path("phase8_perf_buffer_poll.zig"),',
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def fixture_text(rel: str) -> str:
    markers = REQUIRED_MARKERS.get(rel)
    if markers is None:
        return "# fixture\n"
    return "\n".join(markers) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text(rel), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_marker(tmp_root: Path, rel: str, marker: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    replacement = "::drift::"
    updated = original.replace(marker, replacement)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for rel in REQUIRED_FILES:
            (tmp_root / rel).unlink()
            expect_missing_file(f"missing::{rel}", tmp_root, rel)
            write_fixture_root(tmp_root)

        for rel, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                mutate_marker(tmp_root, rel, marker, f"marker::{rel}::{marker}")
                expect_missing_marker(f"marker::{rel}::{marker}", tmp_root, f"{rel}: {marker}")
                write_fixture_root(tmp_root)

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT="
        f"{len(REQUIRED_FILES) + sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current parked Phase 8 libbpf wording and route packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTE_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())