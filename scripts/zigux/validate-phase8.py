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
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-exec-cmd-packet.py",
    "scripts/zigux/check-phase8-help-kallsyms-packet.py",
    "scripts/zigux/validate-phase8.py",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
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
    ".github/workflows/zigux-bootstrap.yml",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/verify.zig",
]

REQUIRED_SEGMENTS = {
    "logging-version-and-errno": "starter_landed",
    "pin-path-helpers": "starter_landed",
    "cpu-mask-parsing": "starter_landed",
    "type-name-helpers": "starter_landed",
    "fdinfo-map-info-helpers": "starter_landed",
    "map-reuse-compatibility": "starter_landed",
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
        "integrated `planDeferredExecvCall()` plus `planDeferredExeclCall()` planner packet",
    ],
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md": [
        "parse_cpu_mask_str()",
        "chunk-reader ingestion",
        "tools/lib/bpf/zigux_segments/manifest.json",
    ],
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md": [
        "\"/proc/%d/fdinfo/%d\" assembly plus bounded fdinfo text parsing",
        "helper-only reused-map compatibility packet",
        "planning-only reopen-attempt disposition",
        "planning-only token-preparation gate",
        "planTokenPreparation()",
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
        "helper-only reused-map name resolution",
        "devmap-aware compatibility checks",
        "planning-only reopen-attempt gating",
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
        "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
        "non-ready wait observations cannot claim record processing",
        "reject impossible post-wait buffer state combinations",
        "python3 scripts/zigux/validate-phase8.py --self-test",
        "python3 scripts/zigux/validate-phase8.py",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "no standalone timer helper",
        "no standalone clockevent helper",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8-test",
        "make -C zigux phase8",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "PHASE8_SEQUENCE=tooling-lane-anti-overlap",
        "### 1. Command lane: parked unless a fresh parity gap appears",
        "### 2. Symbol lane: parked unless symbol parsing or classification moves again",
        "### 3. Libbpf helper lane: the current active Phase 8 implementation surface",
        "### 4. Shared packet wording lane: docs or validator sequencing only",
        "refresh the shared tests-root reminder",
    ],
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md": [
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "mapReuseObservationFromFdinfo()",
        "planTokenPreparation()",
        "resolveReusePinnedMapAttempt()",
        "non-empty pinned path plus compatible fdinfo-derived map info",
        "fd close or ownership semantics",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`make -C zigux phase8-exec-cmd-test`",
        "helper-first, output-stable deferred-exec planning packet",
        "without widening into direct process-launch parity",
        "`kernel/workqueue.c`",
        "if the change touches the shared active Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
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
    "zigux/tests/README.md": [
        "Phase 8 flow",
        "keep the shared Phase 8 tooling packet wired through `zigux/tests/phase8_build.zig`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 help and kallsyms tests",
        "make -C zigux phase8-help-kallsyms-test",
        "zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all",
        "Run Phase 8 tooling tests",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
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
        "phase8-help-kallsyms-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all",
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
        "focused Phase 8 replay keeps the integrated deferred-exec packet reviewable",
    ],
    "zigux/tests/phase8_exec_cmd_only_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
    ],
    "zigux/tests/phase8_file_path_handle_bridge.zig": [
        "phase 8 file-path handle bridge docs keep the bounded fdinfo helper explicit",
        "phase 8 userspace-kernel bridge boundary survey keeps queued bridge work explicit",
        "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard",
        "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard",
        "phase 8 file-path handle bridge helper keeps fdinfo map info parsing compact",
        "phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility",
        "phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit",
        "phase 8 file-path handle bridge helper keeps planning-only token preparation explicit",
        "mapReuseObservationFromFdinfo",
        "resolveReusePinnedMapAttempt",
        "planTokenPreparation",
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
        "Run focused Phase 8 help and kallsyms tests",
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
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8-libbpf-segment-tests",
        "phase8-libbpf-segment-verify-tests",
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
        "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
        "non-ready wait observations cannot claim record processing",
        "phase 8 perf-buffer poll helper keeps the final return-path choice explicit",
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
        "pub fn mapReuseObservationFromFdinfo",
        "pub fn summarizeMapReuseCompatibility",
        "pub fn resolveReusePinnedMapAttempt",
        "pub fn planTokenPreparation",
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
        "pub fn planDeferredExecvCall",
        "pub fn planDeferredExeclCall",
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


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel in FIXTURE_OVERRIDES:
            text = FIXTURE_OVERRIDES[rel]
        else:
            text = "\n".join(REQUIRED_MARKERS.get(rel, ["# fixture"])) + "\n"
        path.write_text(text, encoding="utf-8")


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

    assert segments is not None
    seen: dict[str, str] = {}
    for item in segments:
        if not isinstance(item, dict):
            return [f"{MANIFEST_PATH}: segment_not_object"]
        slug = item.get("slug")
        status = item.get("status")
        if not isinstance(slug, str):
            return [f"{MANIFEST_PATH}: segment_missing_slug"]
        if not isinstance(status, str):
            return [f"{MANIFEST_PATH}: segment_missing_status:{slug}"]
        seen[slug] = status

    manifest_errors: list[str] = []
    for slug, status in REQUIRED_SEGMENTS.items():
        observed = seen.get(slug)
        if observed is None:
            manifest_errors.append(f"{MANIFEST_PATH}: missing_slug:{slug}")
        elif observed != status:
            manifest_errors.append(
                f"{MANIFEST_PATH}: wrong_status:{slug}:{status}:{observed}"
            )
    return manifest_errors


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    marker_errors = collect_missing_markers(root)
    marker_errors.extend(collect_exact_section_errors(root))
    return [], marker_errors, collect_manifest_errors(root)


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
        ("missing_help_kallsyms_checker", "scripts/zigux/check-phase8-help-kallsyms-packet.py"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        (
            "missing_tooling_lane_sequencing",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        ),
        ("missing_exec_cmd_helper", "tools/lib/subcmd/exec-cmd.zig"),
        ("missing_help_helper", "tools/lib/subcmd/help.zig"),
        ("missing_kallsyms_helper", "tools/lib/symbol/kallsyms.zig"),
        ("missing_exec_cmd_test", "zigux/tests/phase8_exec_cmd.zig"),
        ("missing_exec_cmd_only_build", "zigux/tests/phase8_exec_cmd_only_build.zig"),
        ("missing_manifest", MANIFEST_PATH),
        ("missing_libbpf_verify_helper", "tools/lib/bpf/zigux_segments/verify.zig"),
    ]

    marker_cases = [
        (
            "file_path_bridge_slice_reuse_packet",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
            "helper-only reused-map compatibility packet",
            "helper-only map packet",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: helper-only reused-map compatibility packet",
        ),
        (
            "file_path_bridge_slice_reopen_disposition",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
            "planning-only reopen-attempt disposition",
            "planning-only reopen summary",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: planning-only reopen-attempt disposition",
        ),
        (
            "file_path_bridge_slice_token_preparation_gate",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
            "planning-only token-preparation gate",
            "planning-only token gate",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: planning-only token-preparation gate",
        ),
        (
            "file_path_bridge_slice_token_preparation_export",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
            "planTokenPreparation()",
            "planTokenPrep()",
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md: planTokenPreparation()",
        ),
        (
            "libbpf_survey_reuse_name_resolution",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "helper-only reused-map name resolution",
            "helper-only map name resolution",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: helper-only reused-map name resolution",
        ),
        (
            "perf_buffer_poll_slice_validator_self_test",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "python3 scripts/zigux/validate-phase8.py --self-test",
            "python3 scripts/zigux/validate-phase8.py --smoke",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: python3 scripts/zigux/validate-phase8.py --self-test",
        ),
        (
            "perf_buffer_poll_slice_focused_build_gate",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
            "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_build.zig --summary all",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        ),
        (
            "bridge_boundary_fdinfo_observation_handoff",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
            "mapReuseObservationFromFdinfo()",
            "mapReuseObservation()",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: mapReuseObservationFromFdinfo()",
        ),
        (
            "bridge_boundary_non_empty_path_gate",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
            "non-empty pinned path plus compatible fdinfo-derived map info",
            "compatible fdinfo-derived map info",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md: non-empty pinned path plus compatible fdinfo-derived map info",
        ),
        (
            "phase8_bridge_test_observation_replay",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility",
            "phase 8 file-path handle bridge helper keeps reuse observations explicit",
            "zigux/tests/phase8_file_path_handle_bridge.zig: phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility",
        ),
        (
            "phase8_bridge_test_helper_call",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "mapReuseObservationFromFdinfo",
            "mapReuseObservation",
            "zigux/tests/phase8_file_path_handle_bridge.zig: mapReuseObservationFromFdinfo",
        ),
        (
            "phase8_bridge_test_reopen_plan_replay",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit",
            "phase 8 file-path handle bridge helper keeps reopen attempts compact",
            "zigux/tests/phase8_file_path_handle_bridge.zig: phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit",
        ),
        (
            "phase8_bridge_test_token_preparation",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "phase 8 file-path handle bridge helper keeps planning-only token preparation explicit",
            "phase 8 file-path handle bridge helper keeps token preparation compact",
            "zigux/tests/phase8_file_path_handle_bridge.zig: phase 8 file-path handle bridge helper keeps planning-only token preparation explicit",
        ),
        (
            "phase8_bridge_test_reopen_helper_call",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "resolveReusePinnedMapAttempt",
            "resolvePinnedMapAttempt",
            "zigux/tests/phase8_file_path_handle_bridge.zig: resolveReusePinnedMapAttempt",
        ),
        (
            "phase8_bridge_test_token_helper_call",
            "zigux/tests/phase8_file_path_handle_bridge.zig",
            "planTokenPreparation",
            "planTokenFlow",
            "zigux/tests/phase8_file_path_handle_bridge.zig: planTokenPreparation",
        ),
        (
            "phase8_perf_buffer_poll_test_counted_ready_guard",
            "zigux/tests/phase8_perf_buffer_poll.zig",
            "ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
            "ready-buffer processing attempts cannot exceed counted ready buffers",
            "zigux/tests/phase8_perf_buffer_poll.zig: ready-buffer processing attempts cannot exceed counted ready buffers before any broader observed-event budget mismatch",
        ),
        (
            "phase8_perf_buffer_poll_test_nonready_guard",
            "zigux/tests/phase8_perf_buffer_poll.zig",
            "non-ready wait observations cannot claim record processing",
            "non-ready wait observations stay compact",
            "zigux/tests/phase8_perf_buffer_poll.zig: non-ready wait observations cannot claim record processing",
        ),
        (
            "phase8_perf_buffer_poll_test_final_return_path",
            "zigux/tests/phase8_perf_buffer_poll.zig",
            "phase 8 perf-buffer poll helper keeps the final return-path choice explicit",
            "phase 8 perf-buffer poll helper keeps the return choice compact",
            "zigux/tests/phase8_perf_buffer_poll.zig: phase 8 perf-buffer poll helper keeps the final return-path choice explicit",
        ),
        (
            "phase8_libbpf_segments_only_build_verify_module",
            "zigux/tests/phase8_libbpf_segments_only_build.zig",
            "../../tools/lib/bpf/zigux_segments/verify.zig",
            "../../tools/lib/bpf/zigux_segments/verify_missing.zig",
            "zigux/tests/phase8_libbpf_segments_only_build.zig: ../../tools/lib/bpf/zigux_segments/verify.zig",
        ),
        (
            "bridge_helper_observation_export",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            "pub fn mapReuseObservationFromFdinfo",
            "pub fn mapReuseObservation",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig: pub fn mapReuseObservationFromFdinfo",
        ),
        (
            "bridge_helper_compat_summary_export",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            "pub fn summarizeMapReuseCompatibility",
            "pub fn summarizeReuseCompatibility",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig: pub fn summarizeMapReuseCompatibility",
        ),
        (
            "bridge_helper_reopen_plan_export",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            "pub fn resolveReusePinnedMapAttempt",
            "pub fn resolvePinnedMapAttempt",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig: pub fn resolveReusePinnedMapAttempt",
        ),
        (
            "bridge_helper_token_preparation_export",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            "pub fn planTokenPreparation",
            "pub fn prepareTokenPlan",
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig: pub fn planTokenPreparation",
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
    print(
        f"PHASE8_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
