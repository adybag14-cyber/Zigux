#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase8.py",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "zigux/Makefile",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_logging.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "zigux/tests/phase8_pin_path.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
]

REQUIRED_SEGMENTS = {
    "logging-version-and-errno": "starter_landed",
    "pin-path-helpers": "starter_landed",
    "cpu-mask-parsing": "starter_landed",
    "type-name-helpers": "starter_landed",
    "fdinfo-map-info-helpers": "ready_next",
    "map-reuse-compatibility": "ready_next",
    "file-path-and-handle-bridge": "deferred_high_risk",
    "perf-buffer-online-cpu-routing": "deferred_high_risk",
    "skeleton-population": "blocked_on_object_model",
    "object-and-elf-loader": "deferred_high_risk",
    "btf-relocation-and-program-load": "deferred_high_risk",
    "perf-buffer-poll-bookkeeping": "starter_landed",
}

MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"

EXACT_ONCE_SECTION_MARKERS = {
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        {
            "start": "product boundary:\n",
            "end": "\n## Why this slice exists",
            "needle": "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
        },
    ],
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-bpf-type-names-slice.md": [
        "libbpf_bpf_{attach,link,map,prog}_type_str()",
        "dense table lookups with stable output behavior",
        "zigux/tests/phase8_bpf_type_names.zig",
    ],
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md": [
        "parse_cpu_mask_str()",
        "chunk-reader ingestion",
        "tools/lib/bpf/zigux_segments/manifest.json",
    ],
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md": [
        "\"/proc/%d/fdinfo/%d\" assembly plus bounded fdinfo text parsing",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "no direct procfs reads",
        "no `bpf_obj_get()` reopen flow",
    ],
    "Documentation/zigux/phase8-help-slice.md": [
        "serious repo-hosted tooling",
        "output-stable tooling behavior",
        "zigux/tests/phase8_help_only_build.zig",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
    ],
    "Documentation/zigux/phase8-kallsyms-slice.md": [
        "PHASE8_SLICE=kallsyms-parse-wrapper-parked",
        "helper-first expansion",
        "output-stable tooling behavior",
        "one direct `kallsymsParse()` wrapper",
        "zigux/tests/phase8_kallsyms_only_build.zig",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
        "make -C zigux phase8-libbpf-segments-test",
        "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "perf_buffer__poll(timeout_ms)",
        "wait-result classification",
        "ready-buffer processing attempts cannot exceed observed ready events",
        "no standalone timer helper",
        "no standalone clockevent helper",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8-test",
        "make -C zigux phase8",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "planTokenPreparation()",
        "resolveReusePinnedMapAttempt()",
        "fd close or ownership semantics",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "Documentation/zigux/phase8-help-slice.md",
        "Documentation/zigux/phase8-kallsyms-slice.md",
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "zigux/tests/phase8_cpu_mask.zig",
        "zigux/tests/phase8_help.zig",
        "zigux/tests/phase8_help_only_build.zig",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "zigux/tests/phase8_kallsyms.zig",
        "zigux/tests/phase8_kallsyms_only_build.zig",
        "zigux/tests/phase8_logging.zig",
        "zigux/tests/phase8_pin_path.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "make -C zigux phase8-help-test",
        "make -C zigux phase8-kallsyms-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
        "phase8-help-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
        "phase8-kallsyms-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all",
        "phase8-libbpf-segments-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-perf-buffer-poll-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "phase8-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all",
        "phase8: phase8-validate phase8-test",
    ],
    "zigux/tests/phase8_bpf_type_names.zig": [
        "phase 8 bpf type-name segment exposes libbpf string helpers",
        "trace_fsession",
        "map_type_names.len",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/subcmd/help.zig",
        "\"phase8_help.zig\"",
        "phase8-help-tests",
        "../../tools/lib/symbol/kallsyms.zig",
        "\"phase8_kallsyms.zig\"",
        "phase8-kallsyms-tests",
        "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "\"phase8_cpu_mask.zig\"",
        "phase8-cpu-mask-tests",
        "../../tools/lib/bpf/zigux_segments/logging.zig",
        "\"phase8_logging.zig\"",
        "phase8-logging-tests",
        "../../tools/lib/bpf/zigux_segments/pin_path.zig",
        "\"phase8_pin_path.zig\"",
        "phase8-pin-path-tests",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
        "../../tools/lib/bpf/zigux_segments/type_names.zig",
        "\"phase8_bpf_type_names.zig\"",
        "phase8-bpf-type-names-tests",
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "\"phase8_file_path_handle_bridge.zig\"",
        "phase8-file-path-handle-bridge-tests",
    ],
    "zigux/tests/phase8_cpu_mask.zig": [
        "phase 8 cpu mask starter slice parses dense masks and counts possible CPUs",
        "phase 8 cpu mask reader interface accepts chunked sysfs-style input",
        "countPossibleCpus(parsed.values)",
    ],
    "zigux/tests/phase8_help.zig": [
        "phase 8 help slice note keeps helper-first output-stable tooling posture explicit",
        "output-stable pretty-print emission",
        "full `cmd_help()`-adjacent CLI surface",
    ],
    "zigux/tests/phase8_file_path_handle_bridge.zig": [
        "phase 8 file-path handle bridge docs keep the bounded fdinfo helper explicit",
        "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard",
        "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard",
        "phase 8 file-path handle bridge helper keeps fdinfo map info parsing compact",
        "map-reuse-compatibility remains queued",
    ],
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "\"phase8_file_path_handle_bridge.zig\"",
        "phase8-file-path-handle-bridge-tests",
    ],
    "zigux/tests/phase8_help_kallsyms_only_build.zig": [
        "\"Documentation/zigux/phase8-kallsyms-slice.md\"",
        "\"Documentation/zigux/phase8-help-slice.md\"",
        "\"phase8_help.zig\"",
        "\"phase8_kallsyms.zig\"",
        "phase8-help-tests",
        "phase8-kallsyms-tests",
    ],
    "zigux/tests/phase8_help_only_build.zig": [
        "\"Documentation/zigux/phase8-help-slice.md\"",
        "../../tools/lib/subcmd/help.zig",
        "\"phase8_help.zig\"",
        "phase8-help-tests",
    ],
    "zigux/tests/phase8_kallsyms.zig": [
        "phase 8 kallsyms slice note keeps helper-first output-stable tooling posture explicit",
        "PHASE8_SLICE=kallsyms-parse-wrapper-parked",
        "one direct `kallsymsParse()` wrapper",
    ],
    "zigux/tests/phase8_kallsyms_only_build.zig": [
        "\"Documentation/zigux/phase8-kallsyms-slice.md\"",
        "../../tools/lib/symbol/kallsyms.zig",
        "\"phase8_kallsyms.zig\"",
        "phase8-kallsyms-tests",
    ],
    "zigux/tests/phase8_libbpf_segments.zig": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
    ],
    "zigux/tests/phase8_libbpf_segments_only_build.zig": [
        "\"phase8_libbpf_segments.zig\"",
        "phase8-libbpf-segment-tests",
    ],
    "zigux/tests/phase8_logging.zig": [
        "phase 8 logging segment keeps libbpf log-level parsing bounded and explicit",
        "logging.libbpfVersionString()",
        "Kernel verifier blocks program loading",
    ],
    "zigux/tests/phase8_perf_buffer_poll.zig": [
        "no standalone timer helper",
        "no standalone clockevent helper",
        "ready-buffer processing attempts cannot exceed observed ready events",
    ],
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig": [
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "\"phase8_perf_buffer_poll.zig\"",
        "phase8-perf-buffer-poll-tests",
    ],
    "zigux/tests/phase8_pin_path.zig": [
        "phase 8 pin-path segment keeps map-path joining bounded and explicit",
        "buildValidatedSanitizedMapPinPath",
        "error.NameTooLong",
    ],
    "tools/lib/bpf/zigux_segments/cpu_mask.zig": [
        "pub fn parseCpuMaskString",
        "pub fn parseCpuMaskFromReader",
        "pub fn countPossibleCpus",
        "error.InvalidReadCount",
    ],
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig": [
        "pub fn buildProcFdinfoPath",
        "pub fn parseFdinfoMapInfo",
        "pub fn summarizeFdinfoMapInfo",
        "map_flags",
        "/proc/{d}/fdinfo/{d}",
    ],
    "tools/lib/bpf/zigux_segments/logging.zig": [
        "pub fn resolveMinPrintLevel",
        "pub fn libbpfVersionString",
        "pub fn formatErrorString",
        "Kernel verifier blocks program loading",
    ],
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": [
        "summarizePollExecution",
        "ReadyBufferProcessingExceedsReadyCount",
        "ReadyBufferProcessingExceedsObservedEvents",
    ],
    "tools/lib/bpf/zigux_segments/pin_path.zig": [
        "pub const default_bpf_fs_path",
        "pub fn validatePinRootPath",
        "pub fn buildValidatedSanitizedMapPinPath",
    ],
    "tools/lib/bpf/zigux_segments/type_names.zig": [
        "pub fn libbpfBpfAttachTypeStr",
        "pub fn libbpfBpfLinkTypeStr",
        "pub fn libbpfBpfMapTypeStr",
        "pub fn libbpfBpfProgTypeStr",
        "trace_fsession",
        "insn_array",
    ],
}


def build_manifest_fixture() -> str:
    return json.dumps(
        {
            "segments": [
                {"slug": slug, "status": status}
                for slug, status in REQUIRED_SEGMENTS.items()
            ]
        },
        indent=2,
    ) + "\n"


def build_phase8_libbpf_survey_fixture() -> str:
    product_boundary = "\n".join(
        [
            "product boundary:",
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`",
        ]
    )
    trailing_markers = "\n".join(
        REQUIRED_MARKERS["Documentation/zigux/phase8-libbpf-segment-survey.md"]
    )
    return f"{product_boundary}\n\n## Why this slice exists\n{trailing_markers}\n"


FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase8.py": "# fixture\n",
    MANIFEST_PATH: build_manifest_fixture(),
    "Documentation/zigux/phase8-libbpf-segment-survey.md": build_phase8_libbpf_survey_fixture(),
    "tools/lib/bpf/zigux_segments/cpu_mask.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/cpu_mask.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/logging.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/logging.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/pin_path.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/pin_path.zig"]
    )
    + "\n",
    "tools/lib/bpf/zigux_segments/type_names.zig": "\n".join(
        REQUIRED_MARKERS["tools/lib/bpf/zigux_segments/type_names.zig"]
    )
    + "\n",
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def collect_exact_section_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, section_specs in EXACT_ONCE_SECTION_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for spec in section_specs:
            start = text.find(spec["start"])
            if start == -1:
                errors.append(f"{rel}: missing_section_start:{spec['start'].strip()}")
                continue

            section_start = start + len(spec["start"])
            end = text.find(spec["end"], section_start)
            if end == -1:
                errors.append(f"{rel}: missing_section_end:{spec['end'].strip()}")
                continue

            section = text[section_start:end]
            if section.count(spec["needle"]) != 1:
                errors.append(
                    f"{rel}: exact_once_section_marker:{spec['needle'].rstrip()}"
                )
    return errors


def load_manifest_segments(root: Path) -> tuple[list[object] | None, list[str]]:
    manifest_path = root / MANIFEST_PATH
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, [f"{MANIFEST_PATH}: invalid_json"]

    if not isinstance(payload, dict):
        return None, [f"{MANIFEST_PATH}: manifest_not_object"]

    segments = payload.get("segments")
    if not isinstance(segments, list):
        return None, [f"{MANIFEST_PATH}: segments_not_list"]

    return segments, []


def collect_manifest_errors(root: Path) -> list[str]:
    segments, errors = load_manifest_segments(root)
    if errors:
        return errors

    manifest_errors: list[str] = []
    seen: dict[str, int] = {}
    segment_status: dict[str, str] = {}

    assert segments is not None
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            manifest_errors.append(f"{MANIFEST_PATH}: segment_{index}_not_object")
            continue

        slug = segment.get("slug")
        if not isinstance(slug, str):
            manifest_errors.append(f"{MANIFEST_PATH}: segment_{index}_invalid_slug")
            continue

        status = segment.get("status")
        if not isinstance(status, str):
            manifest_errors.append(f"{MANIFEST_PATH}: {slug}: invalid_status")
            continue

        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] == 1:
            segment_status[slug] = status

    for slug, count in sorted(seen.items()):
        if count > 1:
            manifest_errors.append(f"{MANIFEST_PATH}: duplicate_slug:{slug}:{count}")

    for slug, expected_status in REQUIRED_SEGMENTS.items():
        if slug not in seen:
            manifest_errors.append(f"{MANIFEST_PATH}: missing_slug:{slug}")
            continue
        actual_status = segment_status[slug]
        if actual_status != expected_status:
            manifest_errors.append(
                f"{MANIFEST_PATH}: wrong_status:{slug}:{expected_status}:{actual_status}"
            )

    return manifest_errors


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return [], missing_markers, []

    exact_section_errors = collect_exact_section_errors(root)
    if exact_section_errors:
        return [], exact_section_errors, []

    return [], [], collect_manifest_errors(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, manifest_errors = validate(tmp_root)
    assert missing_markers == [], case
    assert manifest_errors == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, manifest_errors = validate(tmp_root)
    assert missing_files == [], case
    assert manifest_errors == [], case
    assert missing_markers == [marker], case


def expect_manifest_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers, manifest_errors = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert manifest_errors == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_validator", "scripts/zigux/validate-phase8.py"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_phase8_help_note", "Documentation/zigux/phase8-help-slice.md"),
        ("missing_phase8_kallsyms_note", "Documentation/zigux/phase8-kallsyms-slice.md"),
        ("missing_phase8_bpf_type_names_note", "Documentation/zigux/phase8-bpf-type-names-slice.md"),
        ("missing_phase8_libbpf_cpu_mask_note", "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md"),
        ("missing_phase8_file_path_handle_bridge_note", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"),
        ("missing_phase8_perf_buffer_poll_note", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_phase8_bridge_boundary_note", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"),
        ("missing_phase8_manifest", MANIFEST_PATH),
        ("missing_phase8_cpu_mask_test", "zigux/tests/phase8_cpu_mask.zig"),
        ("missing_phase8_file_path_handle_bridge_test", "zigux/tests/phase8_file_path_handle_bridge.zig"),
        ("missing_phase8_file_path_handle_bridge_only_build", "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
        ("missing_phase8_help_test", "zigux/tests/phase8_help.zig"),
        ("missing_phase8_help_only_build", "zigux/tests/phase8_help_only_build.zig"),
        ("missing_phase8_help_kallsyms_only_build", "zigux/tests/phase8_help_kallsyms_only_build.zig"),
        ("missing_phase8_kallsyms_test", "zigux/tests/phase8_kallsyms.zig"),
        ("missing_phase8_kallsyms_only_build", "zigux/tests/phase8_kallsyms_only_build.zig"),
        ("missing_phase8_bpf_type_names_test", "zigux/tests/phase8_bpf_type_names.zig"),
        ("missing_phase8_libbpf_segments_only_build", "zigux/tests/phase8_libbpf_segments_only_build.zig"),
        ("missing_phase8_logging_test", "zigux/tests/phase8_logging.zig"),
        ("missing_phase8_perf_buffer_poll_test", "zigux/tests/phase8_perf_buffer_poll.zig"),
        ("missing_phase8_perf_buffer_poll_only_build", "zigux/tests/phase8_perf_buffer_poll_only_build.zig"),
        ("missing_phase8_pin_path_test", "zigux/tests/phase8_pin_path.zig"),
        ("missing_cpu_mask_helper", "tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        ("missing_file_path_handle_bridge_helper", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
        ("missing_logging_helper", "tools/lib/bpf/zigux_segments/logging.zig"),
        ("missing_pin_path_helper", "tools/lib/bpf/zigux_segments/pin_path.zig"),
        ("missing_type_names_helper", "tools/lib/bpf/zigux_segments/type_names.zig"),
        ("missing_perf_buffer_poll_helper", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    ]

    marker_cases = [
        ("scripts_readme_help_note", "scripts/zigux/README.md", "Documentation/zigux/phase8-help-slice.md", "", "scripts/zigux/README.md: Documentation/zigux/phase8-help-slice.md"),
        ("scripts_readme_kallsyms_note", "scripts/zigux/README.md", "Documentation/zigux/phase8-kallsyms-slice.md", "", "scripts/zigux/README.md: Documentation/zigux/phase8-kallsyms-slice.md"),
        ("scripts_readme_cpu_mask_note", "scripts/zigux/README.md", "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md", "", "scripts/zigux/README.md: Documentation/zigux/phase8-libbpf-cpu-mask-slice.md"),
        ("scripts_readme_file_path_handle_bridge_test", "scripts/zigux/README.md", "zigux/tests/phase8_file_path_handle_bridge.zig", "", "scripts/zigux/README.md: zigux/tests/phase8_file_path_handle_bridge.zig"),
        ("scripts_readme_file_path_handle_bridge_build", "scripts/zigux/README.md", "zigux/tests/phase8_file_path_handle_bridge_only_build.zig", "", "scripts/zigux/README.md: zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
        ("scripts_readme_help_target", "scripts/zigux/README.md", "make -C zigux phase8-help-test", "make -C zigux phase8-help-shard", "scripts/zigux/README.md: make -C zigux phase8-help-test"),
        ("scripts_readme_kallsyms_target", "scripts/zigux/README.md", "make -C zigux phase8-kallsyms-test", "make -C zigux phase8-symbols-test", "scripts/zigux/README.md: make -C zigux phase8-kallsyms-test"),
        ("makefile_validate_target", "zigux/Makefile", "phase8-validate:", "", "zigux/Makefile: phase8-validate:"),
        ("makefile_self_test_hook", "zigux/Makefile", "scripts/zigux/validate-phase8.py --self-test", "", "zigux/Makefile: scripts/zigux/validate-phase8.py --self-test"),
        ("makefile_help_wrapper_target", "zigux/Makefile", "phase8-help-test:", "", "zigux/Makefile: phase8-help-test:"),
        ("makefile_help_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_help_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all"),
        ("makefile_kallsyms_wrapper_target", "zigux/Makefile", "phase8-kallsyms-test:", "", "zigux/Makefile: phase8-kallsyms-test:"),
        ("makefile_kallsyms_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_kallsyms_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all"),
        ("makefile_libbpf_wrapper_target", "zigux/Makefile", "phase8-libbpf-segments-test:", "", "zigux/Makefile: phase8-libbpf-segments-test:"),
        ("makefile_libbpf_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all"),
        ("makefile_perf_buffer_wrapper_target", "zigux/Makefile", "phase8-perf-buffer-poll-test:", "", "zigux/Makefile: phase8-perf-buffer-poll-test:"),
        ("makefile_perf_buffer_wrapper_command", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_build.zig --summary all", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all"),
        ("makefile_phase8_wrapper", "zigux/Makefile", "phase8: phase8-validate phase8-test", "phase8: phase8-test", "zigux/Makefile: phase8: phase8-validate phase8-test"),
        ("makefile_phase8_shared_summary", "zigux/Makefile", "$(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all", "$(ZIG) build test --build-file zigux/tests/phase8_build.zig", "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all"),
        ("help_note_output_stable", "Documentation/zigux/phase8-help-slice.md", "output-stable tooling behavior", "", "Documentation/zigux/phase8-help-slice.md: output-stable tooling behavior"),
        ("help_note_shared_build", "Documentation/zigux/phase8-help-slice.md", "zigux/tests/phase8_help_kallsyms_only_build.zig", "", "Documentation/zigux/phase8-help-slice.md: zigux/tests/phase8_help_kallsyms_only_build.zig"),
        ("kallsyms_note_slice_marker", "Documentation/zigux/phase8-kallsyms-slice.md", "PHASE8_SLICE=kallsyms-parse-wrapper-parked", "", "Documentation/zigux/phase8-kallsyms-slice.md: PHASE8_SLICE=kallsyms-parse-wrapper-parked"),
        ("kallsyms_note_wrapper_marker", "Documentation/zigux/phase8-kallsyms-slice.md", "one direct `kallsymsParse()` wrapper", "", "Documentation/zigux/phase8-kallsyms-slice.md: one direct `kallsymsParse()` wrapper"),
        ("phase8_help_packet_phrase", "zigux/tests/phase8_help.zig", "output-stable pretty-print emission", "", "zigux/tests/phase8_help.zig: output-stable pretty-print emission"),
        ("phase8_help_only_build_doc_source", "zigux/tests/phase8_help_only_build.zig", "\"Documentation/zigux/phase8-help-slice.md\"", "\"Documentation/zigux/phase8-help-note.md\"", "zigux/tests/phase8_help_only_build.zig: \"Documentation/zigux/phase8-help-slice.md\""),
        ("phase8_help_only_build_root_source", "zigux/tests/phase8_help_only_build.zig", "\"phase8_help.zig\"", "\"phase8_help_drift.zig\"", "zigux/tests/phase8_help_only_build.zig: \"phase8_help.zig\""),
        ("phase8_help_only_build_test_name", "zigux/tests/phase8_help_only_build.zig", "phase8-help-tests", "phase8-help-shard-tests", "zigux/tests/phase8_help_only_build.zig: phase8-help-tests"),
        ("phase8_help_kallsyms_build_help_root", "zigux/tests/phase8_help_kallsyms_only_build.zig", "\"phase8_help.zig\"", "\"phase8_help_drift.zig\"", "zigux/tests/phase8_help_kallsyms_only_build.zig: \"phase8_help.zig\""),
        ("phase8_help_kallsyms_build_kallsyms_root", "zigux/tests/phase8_help_kallsyms_only_build.zig", "\"phase8_kallsyms.zig\"", "\"phase8_kallsyms_drift.zig\"", "zigux/tests/phase8_help_kallsyms_only_build.zig: \"phase8_kallsyms.zig\""),
        ("phase8_help_kallsyms_build_kallsyms_name", "zigux/tests/phase8_help_kallsyms_only_build.zig", "phase8-kallsyms-tests", "phase8-symbol-tests", "zigux/tests/phase8_help_kallsyms_only_build.zig: phase8-kallsyms-tests"),
        ("phase8_kallsyms_packet_phrase", "zigux/tests/phase8_kallsyms.zig", "one direct `kallsymsParse()` wrapper", "", "zigux/tests/phase8_kallsyms.zig: one direct `kallsymsParse()` wrapper"),
        ("phase8_kallsyms_only_build_doc_source", "zigux/tests/phase8_kallsyms_only_build.zig", "\"Documentation/zigux/phase8-kallsyms-slice.md\"", "\"Documentation/zigux/phase8-symbol-slice.md\"", "zigux/tests/phase8_kallsyms_only_build.zig: \"Documentation/zigux/phase8-kallsyms-slice.md\""),
        ("phase8_kallsyms_only_build_root_source", "zigux/tests/phase8_kallsyms_only_build.zig", "\"phase8_kallsyms.zig\"", "\"phase8_kallsyms_drift.zig\"", "zigux/tests/phase8_kallsyms_only_build.zig: \"phase8_kallsyms.zig\""),
        ("phase8_kallsyms_only_build_test_name", "zigux/tests/phase8_kallsyms_only_build.zig", "phase8-kallsyms-tests", "phase8-symbol-tests", "zigux/tests/phase8_kallsyms_only_build.zig: phase8-kallsyms-tests"),
        ("phase8_build_help_source", "zigux/tests/phase8_build.zig", "\"phase8_help.zig\"", "\"phase8_help_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_help.zig\""),
        ("phase8_build_help_test_name", "zigux/tests/phase8_build.zig", "phase8-help-tests", "phase8-help-shard-tests", "zigux/tests/phase8_build.zig: phase8-help-tests"),
        ("phase8_build_kallsyms_source", "zigux/tests/phase8_build.zig", "\"phase8_kallsyms.zig\"", "\"phase8_kallsyms_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_kallsyms.zig\""),
        ("phase8_build_kallsyms_test_name", "zigux/tests/phase8_build.zig", "phase8-kallsyms-tests", "phase8-symbol-tests", "zigux/tests/phase8_build.zig: phase8-kallsyms-tests"),
        ("phase8_build_cpu_mask_source", "zigux/tests/phase8_build.zig", "\"phase8_cpu_mask.zig\"", "\"phase8_cpu_mask_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_cpu_mask.zig\""),
        ("phase8_build_cpu_mask_test_name", "zigux/tests/phase8_build.zig", "phase8-cpu-mask-tests", "phase8-cpu-tests", "zigux/tests/phase8_build.zig: phase8-cpu-mask-tests"),
        ("phase8_build_logging_source", "zigux/tests/phase8_build.zig", "\"phase8_logging.zig\"", "\"phase8_logging_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_logging.zig\""),
        ("phase8_build_logging_test_name", "zigux/tests/phase8_build.zig", "phase8-logging-tests", "phase8-log-tests", "zigux/tests/phase8_build.zig: phase8-logging-tests"),
        ("phase8_build_pin_path_source", "zigux/tests/phase8_build.zig", "\"phase8_pin_path.zig\"", "\"phase8_pin_path_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_pin_path.zig\""),
        ("phase8_build_pin_path_test_name", "zigux/tests/phase8_build.zig", "phase8-pin-path-tests", "phase8-path-tests", "zigux/tests/phase8_build.zig: phase8-pin-path-tests"),
        ("file_path_handle_note_scope", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md", "\"/proc/%d/fdinfo/%d\" assembly plus bounded fdinfo text parsing", "\"/proc/%d/fdinfo/%d\" only", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: \"/proc/%d/fdinfo/%d\" assembly plus bounded fdinfo text parsing"),
        ("file_path_handle_note_non_goal", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md", "no `bpf_obj_get()` reopen flow", "", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: no `bpf_obj_get()` reopen flow"),
        ("bridge_boundary_note_helper_marker", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", "tools/lib/bpf/zigux_segments/file_path_bridge.zig", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
        ("bridge_boundary_note_reuse_marker", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md", "resolveReusePinnedMapAttempt()", "resolveReusePinnedMapOutcome()", "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: resolveReusePinnedMapAttempt()"),
        ("phase8_build_file_path_handle_source", "zigux/tests/phase8_build.zig", "\"phase8_file_path_handle_bridge.zig\"", "\"phase8_file_path_handle_bridge_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_file_path_handle_bridge.zig\""),
        ("phase8_build_file_path_handle_test_name", "zigux/tests/phase8_build.zig", "phase8-file-path-handle-bridge-tests", "phase8-file-handle-bridge-tests", "zigux/tests/phase8_build.zig: phase8-file-path-handle-bridge-tests"),
        ("phase8_file_path_handle_test_shared_build", "zigux/tests/phase8_file_path_handle_bridge.zig", "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard", "", "zigux/tests/phase8_file_path_handle_bridge.zig: phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard"),
        ("phase8_file_path_handle_only_build_root_source", "zigux/tests/phase8_file_path_handle_bridge_only_build.zig", "\"phase8_file_path_handle_bridge.zig\"", "\"phase8_file_path_handle_bridge_drift.zig\"", "zigux/tests/phase8_file_path_handle_bridge_only_build.zig: \"phase8_file_path_handle_bridge.zig\""),
        ("phase8_file_path_handle_helper_entrypoint", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", "pub fn buildProcFdinfoPath", "pub fn buildFdinfoPath", "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig: pub fn buildProcFdinfoPath"),
        ("survey_timer_boundary", "Documentation/zigux/phase8-libbpf-segment-survey.md", "standalone timer or clockevent helper behavior", "", "Documentation/zigux/phase8-libbpf-segment-survey.md: standalone timer or clockevent helper behavior"),
        ("survey_libbpf_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-libbpf-segments-test", "make -C zigux phase8-libbpf-survey-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-libbpf-segments-test"),
        ("survey_perf_buffer_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-perf-buffer-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("survey_phase8_test_wrapper", "Documentation/zigux/phase8-libbpf-segment-survey.md", "make -C zigux phase8-test", "make -C zigux phase8-shared-test", "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-test"),
        ("survey_libbpf_boundary_exact_line_missing", "Documentation/zigux/phase8-libbpf-segment-survey.md", "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n", "  - `zigux/tests/phase8_libbpf_segments_build.zig`\n", "Documentation/zigux/phase8-libbpf-segment-survey.md: exact_once_section_marker:  - `zigux/tests/phase8_libbpf_segments_only_build.zig`"),
        ("survey_libbpf_boundary_exact_line_duplicate", "Documentation/zigux/phase8-libbpf-segment-survey.md", "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n", "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n", "Documentation/zigux/phase8-libbpf-segment-survey.md: exact_once_section_marker:  - `zigux/tests/phase8_libbpf_segments_only_build.zig`"),
        ("perf_buffer_poll_note_boundary", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "ready-buffer processing attempts cannot exceed observed ready events", "", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: ready-buffer processing attempts cannot exceed observed ready events"),
        ("perf_buffer_poll_note_focused_gate", "Documentation/zigux/phase8-perf-buffer-poll-slice.md", "make -C zigux phase8-perf-buffer-poll-test", "make -C zigux phase8-perf-buffer-test", "Documentation/zigux/phase8-perf-buffer-poll-slice.md: make -C zigux phase8-perf-buffer-poll-test"),
        ("phase8_bpf_type_names_helper_surface", "zigux/tests/phase8_bpf_type_names.zig", "phase 8 bpf type-name segment exposes libbpf string helpers", "", "zigux/tests/phase8_bpf_type_names.zig: phase 8 bpf type-name segment exposes libbpf string helpers"),
        ("phase8_bpf_type_names_dense_table_anchor", "zigux/tests/phase8_bpf_type_names.zig", "map_type_names.len", "", "zigux/tests/phase8_bpf_type_names.zig: map_type_names.len"),
        ("phase8_cpu_mask_reader_anchor", "zigux/tests/phase8_cpu_mask.zig", "phase 8 cpu mask reader interface accepts chunked sysfs-style input", "", "zigux/tests/phase8_cpu_mask.zig: phase 8 cpu mask reader interface accepts chunked sysfs-style input"),
        ("phase8_build_perf_buffer_poll_source", "zigux/tests/phase8_build.zig", "\"phase8_perf_buffer_poll.zig\"", "\"phase8_perf_buffer_poll_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_perf_buffer_poll.zig\""),
        ("phase8_build_perf_buffer_poll_test_name", "zigux/tests/phase8_build.zig", "phase8-perf-buffer-poll-tests", "phase8-perf-buffer-tests", "zigux/tests/phase8_build.zig: phase8-perf-buffer-poll-tests"),
        ("phase8_build_type_names_source", "zigux/tests/phase8_build.zig", "\"phase8_bpf_type_names.zig\"", "\"phase8_bpf_type_names_drift.zig\"", "zigux/tests/phase8_build.zig: \"phase8_bpf_type_names.zig\""),
        ("phase8_build_type_names_test_name", "zigux/tests/phase8_build.zig", "phase8-bpf-type-names-tests", "phase8-bpf-types-tests", "zigux/tests/phase8_build.zig: phase8-bpf-type-names-tests"),
        ("phase8_libbpf_only_build_root_source", "zigux/tests/phase8_libbpf_segments_only_build.zig", "\"phase8_libbpf_segments.zig\"", "\"phase8_libbpf_segments_drift.zig\"", "zigux/tests/phase8_libbpf_segments_only_build.zig: \"phase8_libbpf_segments.zig\""),
        ("phase8_libbpf_only_build_test_name", "zigux/tests/phase8_libbpf_segments_only_build.zig", "phase8-libbpf-segment-tests", "phase8-libbpf-survey-tests", "zigux/tests/phase8_libbpf_segments_only_build.zig: phase8-libbpf-segment-tests"),
        ("phase8_logging_version_anchor", "zigux/tests/phase8_logging.zig", "logging.libbpfVersionString()", "", "zigux/tests/phase8_logging.zig: logging.libbpfVersionString()"),
        ("phase8_perf_buffer_poll_no_timer", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone timer helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone timer helper"),
        ("phase8_perf_buffer_poll_no_clockevent", "zigux/tests/phase8_perf_buffer_poll.zig", "no standalone clockevent helper", "", "zigux/tests/phase8_perf_buffer_poll.zig: no standalone clockevent helper"),
        ("phase8_perf_buffer_only_build_helper_source", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_drift.zig", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: ../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        ("phase8_perf_buffer_only_build_root_source", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "\"phase8_perf_buffer_poll.zig\"", "\"phase8_perf_buffer_poll_drift.zig\"", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: \"phase8_perf_buffer_poll.zig\""),
        ("phase8_perf_buffer_only_build_test_name", "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "phase8-perf-buffer-poll-tests", "phase8-perf-buffer-tests", "zigux/tests/phase8_perf_buffer_poll_only_build.zig: phase8-perf-buffer-poll-tests"),
        ("phase8_pin_path_overflow_anchor", "zigux/tests/phase8_pin_path.zig", "error.NameTooLong", "", "zigux/tests/phase8_pin_path.zig: error.NameTooLong"),
        ("cpu_mask_helper_reader_anchor", "tools/lib/bpf/zigux_segments/cpu_mask.zig", "pub fn parseCpuMaskFromReader", "pub fn parseCpuMaskReader", "tools/lib/bpf/zigux_segments/cpu_mask.zig: pub fn parseCpuMaskFromReader"),
        ("helper_ready_count_guard", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig", "ReadyBufferProcessingExceedsReadyCount", "ReadyBufferCountMismatch", "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig: ReadyBufferProcessingExceedsReadyCount"),
        ("logging_helper_version_anchor", "tools/lib/bpf/zigux_segments/logging.zig", "pub fn libbpfVersionString", "pub fn libbpfVersion", "tools/lib/bpf/zigux_segments/logging.zig: pub fn libbpfVersionString"),
        ("pin_path_helper_validation_anchor", "tools/lib/bpf/zigux_segments/pin_path.zig", "pub fn buildValidatedSanitizedMapPinPath", "pub fn buildSanitizedValidatedMapPinPath", "tools/lib/bpf/zigux_segments/pin_path.zig: pub fn buildValidatedSanitizedMapPinPath"),
        ("type_names_attach_helper", "tools/lib/bpf/zigux_segments/type_names.zig", "pub fn libbpfBpfAttachTypeStr", "pub fn attachTypeStr", "tools/lib/bpf/zigux_segments/type_names.zig: pub fn libbpfBpfAttachTypeStr"),
        ("type_names_table_tail", "tools/lib/bpf/zigux_segments/type_names.zig", "trace_fsession", "trace_session_drift", "tools/lib/bpf/zigux_segments/type_names.zig: trace_fsession"),
    ]

    manifest_cases = [
        ("manifest_invalid_json", "{not json}\n", f"{MANIFEST_PATH}: invalid_json"),
        ("manifest_segments_not_list", json.dumps({"segments": {"slug": "logging-version-and-errno"}}) + "\n", f"{MANIFEST_PATH}: segments_not_list"),
        (
            "manifest_duplicate_slug",
            json.dumps(
                {
                    "segments": [
                        {"slug": "logging-version-and-errno", "status": "starter_landed"},
                        {"slug": "logging-version-and-errno", "status": "starter_landed"},
                        *[
                            {"slug": slug, "status": status}
                            for slug, status in REQUIRED_SEGMENTS.items()
                            if slug != "logging-version-and-errno"
                        ],
                    ]
                },
                indent=2,
            )
            + "\n",
            f"{MANIFEST_PATH}: duplicate_slug:logging-version-and-errno:2",
        ),
        (
            "manifest_missing_slug",
            json.dumps(
                {
                    "segments": [
                        {"slug": slug, "status": status}
                        for slug, status in REQUIRED_SEGMENTS.items()
                        if slug != "cpu-mask-parsing"
                    ]
                },
                indent=2,
            )
            + "\n",
            f"{MANIFEST_PATH}: missing_slug:cpu-mask-parsing",
        ),
        (
            "manifest_wrong_status",
            json.dumps(
                {
                    "segments": [
                        {
                            "slug": slug,
                            "status": ("ready_next" if slug == "perf-buffer-poll-bookkeeping" else status),
                        }
                        for slug, status in REQUIRED_SEGMENTS.items()
                    ]
                },
                indent=2,
            )
            + "\n",
            f"{MANIFEST_PATH}: wrong_status:perf-buffer-poll-bookkeeping:starter_landed:ready_next",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        for case, manifest_text, expected in manifest_cases:
            (tmp_root / MANIFEST_PATH).write_text(manifest_text, encoding="utf-8")
            expect_manifest_error(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    print("PHASE8_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT={len(missing_file_cases) + len(marker_cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 8 repo-hosted tooling packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, manifest_errors = validate(ROOT)
    if missing_files:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_MARKERS_END")
        return 1

    if manifest_errors:
        print("PHASE8_VALIDATION=fail")
        print("PHASE8_MANIFEST_ERRORS_START")
        for item in manifest_errors:
            print(item)
        print("PHASE8_MANIFEST_ERRORS_END")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
