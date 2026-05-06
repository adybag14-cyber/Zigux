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
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-exec-cmd-packet.py",
    "scripts/zigux/validate-phase8.py",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
    "zigux/Makefile",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
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
    "Documentation/zigux/phase8-exec-cmd-slice.md": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "helper-first, output-stable deferred-exec planning",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-exec-cmd-test",
        "stops before any ownership of `execv_cmd()` or `execvp()`",
        "stops before any ownership of `execl_cmd()`",
        "direct varargs launch path",
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
        "make -C zigux phase8-validate",
        "make -C zigux phase8-help-test",
        "zig build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
        "make -C zigux phase8",
        "zigux/tests/phase8_help_only_build.zig",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
    ],
    "Documentation/zigux/phase8-kallsyms-slice.md": [
        "PHASE8_SLICE=kallsyms-parse-wrapper-parked",
        "helper-first expansion",
        "output-stable tooling behavior",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-kallsyms-test",
        "zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all",
        "make -C zigux phase8",
        "one direct `kallsymsParse()` wrapper",
        "zigux/tests/phase8_kallsyms_only_build.zig",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "perf-buffer-online-cpu-routing",
        "standalone timer or clockevent helper behavior",
        "make -C zigux phase8-libbpf-segments-test",
        "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
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
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`make -C zigux phase8-exec-cmd-test`",
        "helper-first, output-stable deferred-exec planning packet",
        "without widening into direct process-launch parity",
        "`kernel/workqueue.c`",
        "if the change touches the shared active Phase 8 libbpf packet",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
        "without widening `perf-buffer-online-cpu-routing` into live epoll",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "Documentation/zigux/phase8-help-slice.md",
        "Documentation/zigux/phase8-kallsyms-slice.md",
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
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
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-help-test",
        "make -C zigux phase8-kallsyms-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-exec-cmd-packet.py",
        "phase8-exec-cmd-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
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
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
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
    "zigux/tests/phase8_exec_cmd.zig": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "shared Phase 8 validator-first route",
        "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit",
        "make -C zigux phase8-validate",
        "helper-first, output-stable deferred-exec planning",
        "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors",
        "`execl_cmd()`",
    ],
    "zigux/tests/phase8_exec_cmd_only_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
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
    "zigux/tests/phase8_help.zig": [
        "phase 8 help slice note keeps helper-first output-stable tooling posture explicit",
        "output-stable pretty-print emission",
        "full `cmd_help()`-adjacent CLI surface",
        "phase8_help_only_build.zig",
        "phase8_help_kallsyms_only_build.zig",
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
        "phase8_kallsyms_only_build.zig",
        "phase8_help_kallsyms_only_build.zig",
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
    "tools/lib/subcmd/exec-cmd.zig": [
        "pub fn buildDeferredExecvCall",
        "pub fn buildDeferredExeclCall",
        "pub fn collectExeclArgs",
        "pub fn choosePwdCwdFromFilesystem",
        "pub const max_execl_slots",
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


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers, manifest_errors = validate(tmp_root)
    assert missing_files == [], case
    assert manifest_errors == [], case
    assert missing_markers == [expected], case


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
        ("missing_exec_cmd_slice", "Documentation/zigux/phase8-exec-cmd-slice.md"),
        ("missing_review_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_exec_cmd_checker", "scripts/zigux/check-phase8-exec-cmd-packet.py"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_exec_cmd_helper", "tools/lib/subcmd/exec-cmd.zig"),
        ("missing_help_helper", "tools/lib/subcmd/help.zig"),
        ("missing_kallsyms_helper", "tools/lib/symbol/kallsyms.zig"),
        ("missing_exec_cmd_test", "zigux/tests/phase8_exec_cmd.zig"),
        ("missing_exec_cmd_only_build", "zigux/tests/phase8_exec_cmd_only_build.zig"),
        ("missing_manifest", MANIFEST_PATH),
    ]

    marker_cases = [
        (
            "exec_cmd_slice_marker",
            "Documentation/zigux/phase8-exec-cmd-slice.md",
            "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
            "PHASE8_SLICE=exec-cmd-drift",
            "Documentation/zigux/phase8-exec-cmd-slice.md: PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        ),
        (
            "exec_cmd_slice_execl_boundary",
            "Documentation/zigux/phase8-exec-cmd-slice.md",
            "stops before any ownership of `execl_cmd()`",
            "stops before any ownership of `execl_launch()`",
            "Documentation/zigux/phase8-exec-cmd-slice.md: stops before any ownership of `execl_cmd()`",
        ),
        (
            "help_slice_make_wrapper",
            "Documentation/zigux/phase8-help-slice.md",
            "make -C zigux phase8-help-test",
            "make -C zigux phase8-help",
            "Documentation/zigux/phase8-help-slice.md: make -C zigux phase8-help-test",
        ),
        (
            "help_slice_build_shard",
            "Documentation/zigux/phase8-help-slice.md",
            "zig build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
            "zig build test --build-file zigux/tests/phase8_help_build.zig --summary all",
            "Documentation/zigux/phase8-help-slice.md: zig build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
        ),
        (
            "kallsyms_slice_make_wrapper",
            "Documentation/zigux/phase8-kallsyms-slice.md",
            "make -C zigux phase8-kallsyms-test",
            "make -C zigux phase8-kallsyms",
            "Documentation/zigux/phase8-kallsyms-slice.md: make -C zigux phase8-kallsyms-test",
        ),
        (
            "kallsyms_slice_build_shard",
            "Documentation/zigux/phase8-kallsyms-slice.md",
            "zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all",
            "zig build test --build-file zigux/tests/phase8_kallsyms_build.zig --summary all",
            "Documentation/zigux/phase8-kallsyms-slice.md: zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all",
        ),
        (
            "review_checklist_exec_cmd_packet",
            "Documentation/zigux/review-checklist.md",
            "if the change touches the parked Phase 8 `exec-cmd` packet",
            "if the change touches the parked Phase 8 `help` packet",
            "Documentation/zigux/review-checklist.md: if the change touches the parked Phase 8 `exec-cmd` packet",
        ),
        (
            "review_checklist_exec_cmd_workqueue_boundary",
            "Documentation/zigux/review-checklist.md",
            "`kernel/workqueue.c`",
            "`kernel/sched/core.c`",
            "Documentation/zigux/review-checklist.md: `kernel/workqueue.c`",
        ),
        (
            "review_checklist_libbpf_packet",
            "Documentation/zigux/review-checklist.md",
            "if the change touches the shared active Phase 8 libbpf packet",
            "if the change touches the shared active Phase 8 cpu-mask packet",
            "Documentation/zigux/review-checklist.md: if the change touches the shared active Phase 8 libbpf packet",
        ),
        (
            "scripts_readme_exec_cmd_checker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase8-exec-cmd-packet.py",
            "scripts/zigux/check-phase8-exec-cmd-gate.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase8-exec-cmd-packet.py",
        ),
        (
            "scripts_readme_exec_cmd_make_route",
            "scripts/zigux/README.md",
            "make -C zigux phase8-exec-cmd-test",
            "make -C zigux phase8-exec-test",
            "scripts/zigux/README.md: make -C zigux phase8-exec-cmd-test",
        ),
        (
            "makefile_exec_cmd_checker_self_test",
            "zigux/Makefile",
            "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
            "scripts/zigux/check-phase8-exec-cmd-gate.py --self-test",
            "zigux/Makefile: scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
        ),
        (
            "makefile_exec_cmd_target",
            "zigux/Makefile",
            "phase8-exec-cmd-test:",
            "phase8-exec-test:",
            "zigux/Makefile: phase8-exec-cmd-test:",
        ),
        (
            "shared_build_exec_cmd_source",
            "zigux/tests/phase8_build.zig",
            "\"phase8_exec_cmd.zig\"",
            "\"phase8_exec_cmd_drift.zig\"",
            "zigux/tests/phase8_build.zig: \"phase8_exec_cmd.zig\"",
        ),
        (
            "shared_build_exec_cmd_name",
            "zigux/tests/phase8_build.zig",
            "phase8-exec-cmd-tests",
            "phase8-exec-tests",
            "zigux/tests/phase8_build.zig: phase8-exec-cmd-tests",
        ),
        (
            "focused_exec_cmd_test_route",
            "zigux/tests/phase8_exec_cmd.zig",
            "make -C zigux phase8-validate",
            "make -C zigux phase8-test",
            "zigux/tests/phase8_exec_cmd.zig: make -C zigux phase8-validate",
        ),
        (
            "focused_exec_cmd_c_anchor_boundary",
            "zigux/tests/phase8_exec_cmd.zig",
            "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors",
            "phase 8 exec-cmd deferred boundary note still matches the live helper packet",
            "zigux/tests/phase8_exec_cmd.zig: phase 8 exec-cmd deferred boundary note still matches the live C helper anchors",
        ),
        (
            "help_test_combined_shard_marker",
            "zigux/tests/phase8_help.zig",
            "phase8_help_kallsyms_only_build.zig",
            "phase8_help_symbol_only_build.zig",
            "zigux/tests/phase8_help.zig: phase8_help_kallsyms_only_build.zig",
        ),
        (
            "focused_exec_cmd_build_name",
            "zigux/tests/phase8_exec_cmd_only_build.zig",
            "phase8-exec-cmd-tests",
            "phase8-exec-tests",
            "zigux/tests/phase8_exec_cmd_only_build.zig: phase8-exec-cmd-tests",
        ),
        (
            "kallsyms_test_combined_shard_marker",
            "zigux/tests/phase8_kallsyms.zig",
            "phase8_help_kallsyms_only_build.zig",
            "phase8_help_symbol_only_build.zig",
            "zigux/tests/phase8_kallsyms.zig: phase8_help_kallsyms_only_build.zig",
        ),
        (
            "helper_deferred_execv",
            "tools/lib/subcmd/exec-cmd.zig",
            "pub fn buildDeferredExecvCall",
            "pub fn buildDeferredExecCall",
            "tools/lib/subcmd/exec-cmd.zig: pub fn buildDeferredExecvCall",
        ),
        (
            "survey_file_path_make_wrapper",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "make -C zigux phase8-file-path-handle-bridge-test",
            "make -C zigux phase8-file-path-handle-bridge",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: make -C zigux phase8-file-path-handle-bridge-test",
        ),
        (
            "survey_file_path_build_shard",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
            "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_build.zig --summary all",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
        ),
        (
            "survey_exact_once_duplicate",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
            "  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n  - `zigux/tests/phase8_libbpf_segments_only_build.zig`\n",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: exact_once_section_marker:  - `zigux/tests/phase8_libbpf_segments_only_build.zig`",
        ),
    ]

    manifest_cases = [
        ("manifest_invalid_json", "{not json}\n", f"{MANIFEST_PATH}: invalid_json"),
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
                            "status": (
                                "ready_next"
                                if slug == "perf-buffer-poll-bookkeeping"
                                else status
                            ),
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
            if "exact_once_section_marker" in expected:
                missing_files, missing_markers, manifest_errors = validate(tmp_root)
                assert missing_files == [], case
                assert manifest_errors == [], case
                assert missing_markers == [expected], case
            else:
                expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        for case, manifest_text, expected in manifest_cases:
            (tmp_root / MANIFEST_PATH).write_text(manifest_text, encoding="utf-8")
            expect_manifest_error(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    print("PHASE8_VALIDATOR_SELF_TEST=pass")
    print(
        "PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases) + len(manifest_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current shared Phase 8 repo-hosted tooling packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run validator self-test cases without reading repo files.",
    )
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