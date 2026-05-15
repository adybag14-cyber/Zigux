#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
VERIFY_HELPER_PATH = "tools/lib/bpf/zigux_segments/verify.zig"
ONLINE_CPU_ROUTING_HELPER_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"

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
    VERIFY_HELPER_PATH,
    ONLINE_CPU_ROUTING_HELPER_PATH,
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
        "Exact 2026-05-15 reread keeps the earlier docs-root reopen cue closed instead of reopening it",
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
        "current shared reminder surfaces already keep the landed bridge-plus-build packet explicit through `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_build.zig`, `zigux/Makefile`, and `scripts/zigux/validate-phase8.py`",
        "current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "advanceOnlineCpuCursor()",
        "summarizeNextOnlineCpuRoute()",
        "summarizeOnlineCpuRouting()",
        "The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.",
        "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        "The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence",
        "The real current gap is now survey truthfulness about the already-landed checker packet, helper-local routing evidence, and the landed bridge-plus-build packet itself, not environment-specific contents-route flakiness or a missing checker rule.",
        "The older mixed-source caveat is now too weak for this packet.",
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`",
        "That same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit",
        "standalone timer or clockevent helper behavior",
        "broader timeout-sensitive routing behavior",
        "Keep the libbpf survey packet parked after this survey-and-route sync unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.",
    ],
    BOUNDARY_SURVEY_PATH: [
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`",
        "deferred `perf-buffer-online-cpu-routing` packet",
        "`/sys/devices/system/cpu/online`",
        "`libbpf_num_possible_cpus()`",
        "online CPU filtering",
        "per-CPU perf-event-array map updates",
        "`perf_event_open()`",
        "perf-buffer ring `mmap()` setup",
        "`PERF_EVENT_IOC_ENABLE` enablement",
        "epoll-backed perf FD registration",
        "poll waits",
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
    VERIFY_HELPER_PATH: [
        "const logging = @import(\"logging.zig\");",
        "const file_path_handle_bridge = @import(\"file_path_handle_bridge.zig\");",
        "fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {",
        'test "helper-first tools/lib/bpf Zigux segments compile together and keep their focused tests live" {',
        'test "helper-first tools/lib/bpf Zigux segments keep the landed bounded entrypoints explicit" {',
        'try expectHasDecl(logging, "resolveMinPrintLevel");',
        'try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");',
        'try expectHasDecl(cpu_mask, "parseCpuMaskString");',
        'try expectHasDecl(type_names, "libbpfBpfMapTypeStr");',
        'try expectHasDecl(file_path_handle_bridge, "planTokenPreparation");',
        'try expectHasDecl(perf_buffer_poll, "summarizePollExecution");',
    ],
    ONLINE_CPU_ROUTING_HELPER_PATH: [
        "pub fn advanceOnlineCpuCursor(",
        "pub fn summarizeNextOnlineCpuRoute(",
        "pub fn summarizeOnlineCpuRouting(",
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

EXPECTED_MANIFEST_SEGMENTS = {
    "fdinfo-map-info-helpers": {
        "status": "starter_landed",
        "kind": "helper_first",
    },
    "map-reuse-compatibility": {
        "status": "starter_landed",
        "kind": "helper_first",
    },
    "perf-buffer-online-cpu-routing": {
        "status": "deferred_high_risk",
        "kind": "interrupt_routing",
    },
    "perf-buffer-poll-bookkeeping": {
        "status": "starter_landed",
        "kind": "helper_adjacent",
    },
}

EXPECTED_ROUTING_WHY_NOW_MARKERS = [
    "online_cpu_routing.zig",
    "cursor and routing-summary helper",
]


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_text_markers(root: Path) -> list[str]:
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


def collect_manifest_problems(root: Path) -> list[str]:
    path = root / MANIFEST_PATH
    if not path.exists():
        return []

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_PATH}: invalid_json:{exc.lineno}:{exc.colno}"]

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        return [f"{MANIFEST_PATH}: segments:not_a_list"]

    by_slug = {
        segment.get("slug"): segment
        for segment in segments
        if isinstance(segment, dict) and isinstance(segment.get("slug"), str)
    }

    problems: list[str] = []
    for slug, expected_fields in EXPECTED_MANIFEST_SEGMENTS.items():
        segment = by_slug.get(slug)
        if segment is None:
            problems.append(f"{MANIFEST_PATH}: missing_segment:{slug}")
            continue
        for field, expected_value in expected_fields.items():
            actual_value = segment.get(field)
            if actual_value != expected_value:
                problems.append(
                    f"{MANIFEST_PATH}: segment:{slug}:{field}:{actual_value!r}:{expected_value!r}"
                )

    routing_segment = by_slug.get("perf-buffer-online-cpu-routing")
    if isinstance(routing_segment, dict):
        why_now = routing_segment.get("why_now")
        if not isinstance(why_now, str):
            problems.append(f"{MANIFEST_PATH}: segment:perf-buffer-online-cpu-routing:why_now:not_a_string")
        else:
            for marker in EXPECTED_ROUTING_WHY_NOW_MARKERS:
                if marker not in why_now:
                    problems.append(
                        f"{MANIFEST_PATH}: segment:perf-buffer-online-cpu-routing:why_now:{marker}"
                    )

    return problems


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    missing_markers = collect_missing_text_markers(root)
    missing_markers.extend(collect_manifest_problems(root))
    return [], missing_markers


def fixture_text(rel: str) -> str:
    if rel == MANIFEST_PATH:
        return (
            json.dumps(
                {
                    "lane_key": "P8-L15",
                    "phase": "Phase 8",
                    "surveyed_commit": "0123456789abcdef0123456789abcdef01234567",
                    "anchor": "tools/lib/bpf/libbpf.c",
                    "segments": [
                        {
                            "slug": "fdinfo-map-info-helpers",
                            "status": "starter_landed",
                            "kind": "helper_first",
                            "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                            "why_now": "fixture",
                        },
                        {
                            "slug": "map-reuse-compatibility",
                            "status": "starter_landed",
                            "kind": "helper_first",
                            "zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                            "why_now": "fixture",
                        },
                        {
                            "slug": "perf-buffer-online-cpu-routing",
                            "status": "deferred_high_risk",
                            "kind": "interrupt_routing",
                            "zigux_destination": "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
                            "why_now": (
                                "The broader online-CPU routing path still combines sysfs reads, "
                                "perf_event_open setup, mmap-backed ring state, map updates, epoll registration, "
                                "and timeout-sensitive polling, but current master already carries the bounded "
                                "online-CPU cursor and routing-summary helper in online_cpu_routing.zig, so the "
                                "setup-side packet stays deferred without pretending that helper-local routing "
                                "evidence is absent."
                            ),
                        },
                        {
                            "slug": "perf-buffer-poll-bookkeeping",
                            "status": "starter_landed",
                            "kind": "helper_adjacent",
                            "zigux_destination": "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                            "why_now": "fixture",
                        },
                    ],
                },
                indent=2,
            )
            + "\n"
        )

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
    updated = original.replace(marker, "::drift::", 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def mutate_manifest(tmp_root: Path, mutator) -> None:
    path = tmp_root / MANIFEST_PATH
    manifest = json.loads(path.read_text(encoding="utf-8"))
    mutator(manifest)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> None:
    text_case_count = len(REQUIRED_FILES) + sum(len(markers) for markers in REQUIRED_MARKERS.values())
    manifest_case_count = 2

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

        def break_status(manifest: dict) -> None:
            for segment in manifest["segments"]:
                if segment["slug"] == "map-reuse-compatibility":
                    segment["status"] = "ready_next"
                    return
            raise AssertionError("missing segment")

        mutate_manifest(tmp_root, break_status)
        expect_missing_marker(
            "manifest::status",
            tmp_root,
            f"{MANIFEST_PATH}: segment:map-reuse-compatibility:status:'ready_next':'starter_landed'",
        )
        write_fixture_root(tmp_root)

        def break_routing_why_now(manifest: dict) -> None:
            for segment in manifest["segments"]:
                if segment["slug"] == "perf-buffer-online-cpu-routing":
                    segment["why_now"] = (
                        "The broader online-CPU routing path still combines sysfs reads, but current "
                        "master already carries the bounded online-CPU cursor and helper evidence "
                        "in online_cpu_routing.zig."
                    )
                    return
            raise AssertionError("missing segment")

        mutate_manifest(tmp_root, break_routing_why_now)
        expect_missing_marker(
            "manifest::routing_why_now",
            tmp_root,
            f"{MANIFEST_PATH}: segment:perf-buffer-online-cpu-routing:why_now:cursor and routing-summary helper",
        )

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT="
        f"{text_case_count + manifest_case_count}"
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
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + len(EXPECTED_MANIFEST_SEGMENTS) + len(EXPECTED_ROUTING_WHY_NOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())