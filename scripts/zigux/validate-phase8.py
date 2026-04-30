#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase8.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_logging.zig",
    "zigux/tests/phase8_pin_path.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
    ".github/workflows/zigux-bootstrap.yml",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def require_match(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise ValueError(label)
    return match.group(1)


required_make_markers = [
    "PHONY += phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-test phase8",
    "phase8-validate:",
    "scripts/zigux/validate-phase8.py",
    "phase8-exec-cmd-test:",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "phase8-help-test:",
    "zigux/tests/phase8_help_only_build.zig",
    "phase8-kallsyms-test:",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "phase8-test:",
    "zigux/tests/phase8_build.zig --summary all",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-test",
]

required_workflow_markers = [
    "Validate Phase 8 tooling gates",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 exec-cmd tests",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "Run focused Phase 8 help tests",
    "zigux/tests/phase8_help_only_build.zig",
    "Run focused Phase 8 kallsyms tests",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "Run focused Phase 8 libbpf segment survey tests",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "Run Phase 8 tooling tests",
    "zigux/tests/phase8_build.zig",
]

required_script_readme_markers = [
    "validate-phase8.py",
    "Phase 8 flow",
    "make -C zigux phase8-validate",
    "phase8_libbpf_segments_only_build.zig",
    "phase8_build.zig",
    "phase8-exec-cmd-slice.md",
    "phase8-userspace-kernel-bridge-boundary-survey.md",
    "tools/lib/subcmd/exec-cmd.zig",
    "deferred execution",
    "execvp()",
    "kernel/workqueue.c",
    "phase8-libbpf-segment-survey.md",
    "cpu_mask.zig",
    "type_names.zig",
    "make -C zigux phase8-test",
    "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
]

required_tests_readme_markers = [
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_logging.zig",
    "zigux/tests/phase8_pin_path.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "scripts/zigux/validate-phase8.py",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
]

required_doc_readme_markers = [
    "Phase 8 notes",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "python3 scripts/zigux/validate-phase8.py",
    "make -C zigux phase8-validate",
    "make -C zigux phase8",
]

required_review_checklist_markers = [
    "parked Phase 8 `exec-cmd` helper packet",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "zigux/tests/phase8_exec_cmd.zig",
    "deferred execution helper-only",
    "kernel/workqueue.c",
    "`execv_cmd()`",
    "`execl_cmd()`",
    "`execvp()`",
    "queue ownership",
    "scheduler-facing transport claims",
    "parked Phase 8 `help` packet",
    "Documentation/zigux/phase8-help-slice.md",
    "zigux/tests/phase8_help.zig",
    "`load_command_list()`",
    "`pretty_print_string_list()`",
    "`list_commands()`",
    "`opendir()` or `readdir()` parity",
    "raw `ioctl()` terminal probing",
    "parked Phase 8 `kallsyms` parser packet",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "zigux/tests/phase8_kallsyms.zig",
    "chunked discard-after-boundary handling",
    "`kallsyms__parse()`",
    "`api/io.h`",
    "downstream ELF-emission behavior",
]

required_phase8_build_markers = [
    "../../tools/lib/subcmd/exec-cmd.zig",
    "../../tools/lib/subcmd/help.zig",
    "../../tools/lib/symbol/kallsyms.zig",
    "../../tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "../../tools/lib/bpf/zigux_segments/logging.zig",
    "../../tools/lib/bpf/zigux_segments/pin_path.zig",
    "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "../../tools/lib/bpf/zigux_segments/type_names.zig",
    "phase8_exec_cmd.zig",
    "phase8_help.zig",
    "phase8_kallsyms.zig",
    "phase8_cpu_mask.zig",
    "phase8-cpu-mask-tests",
    "phase8_logging.zig",
    "phase8-logging-tests",
    "phase8_pin_path.zig",
    "phase8-pin-path-tests",
    "phase8_file_path_handle_bridge.zig",
    "phase8-file-path-handle-bridge-tests",
    "phase8_libbpf_segments.zig",
    "phase8_bpf_type_names.zig",
    "phase8-bpf-type-names-tests",
]

required_phase8_exec_cmd_only_build_markers = [
    "phase8_exec_cmd.zig",
    "phase8-exec-cmd-tests",
    "Run focused Phase 8 exec-cmd tests",
]

required_phase8_help_only_build_markers = [
    "phase8_help.zig",
    "phase8-help-tests",
    "Run focused Phase 8 help tests",
]

required_phase8_kallsyms_only_build_markers = [
    "phase8_kallsyms.zig",
    "phase8-kallsyms-tests",
    "Run focused Phase 8 kallsyms tests",
]

required_phase8_libbpf_segments_only_build_markers = [
    "phase8_libbpf_segments.zig",
    "phase8-libbpf-segment-tests",
    "Run focused Phase 8 libbpf segment survey tests",
]

required_survey_markers = [
    "The manifest currently records eleven bounded segments:",
    "- `map-reuse-compatibility`",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "fdinfo-map-info-helpers",
    "map-reuse-compatibility",
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "phase8_file_path_handle_bridge.zig",
    "path construction",
    "map reuse compatibility",
    "DEVMAP readonly-prog",
    "planTokenPreparation()",
    "optional-versus-mandatory bpffs intent",
    "classifyTokenPreparationFailure()",
    "skip_optional_missing_delegation",
    "fail-fast boundary",
    "default `/sys/fs/bpf` optional probing",
    "text parsing",
    "/proc/.../fdinfo",
    "`open()` or `close()` ownership",
    "`bpf_obj_get()` reopen flows",
    "`bpf_token_create()` handle lifecycle parity",
    "bpf_object_prepare_token()",
    "bpf_object__reuse_map()",
    "bpf_get_map_info_from_fdinfo()",
    "real procfs reads",
    "bpffs opens",
    "fd close or ownership semantics",
    "online CPU filtering",
    "interrupt-routing-sensitive timing boundary",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_logging.zig",
    "zigux/tests/phase8_pin_path.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "make -C zigux phase8",
]

required_bridge_boundary_markers = [
    "PHASE8_SLICE=userspace-kernel-bridge-boundary-survey",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "planTokenPreparation()",
    "classifyTokenPreparationFailure()",
    "execvp()",
    "environment reads or writes",
    "opendir()",
    "readdir()",
    "ioctl()",
    "/proc/.../fdinfo",
    "`bpf_obj_get()` reopen flows",
    "`bpf_token_create()` handle lifecycle parity",
    "`open()` or `close()` ownership",
    "perf-buffer-online-cpu-routing",
    "/sys/devices/system/cpu/online",
    "cached `/sys/devices/system/cpu/possible` counts",
    "libbpf_num_possible_cpus()",
    "per-CPU perf-event-array map updates",
    "epoll-backed perf FD registration",
    "perf_buffer__poll(timeout_ms)",
    "ready-buffer counts",
    "no standalone timer helper",
    "no standalone clockevent helper",
    "skip_optional_missing_delegation",
    "mandatory `fail`",
    "python3 scripts/zigux/validate-phase8.py",
    "make -C zigux phase8-validate",
    "zig build test --build-file zigux/tests/phase8_build.zig",
]

required_exec_cmd_slice_markers = [
    "PHASE8_SLICE=exec-cmd-tooling-starter",
    "tools/lib/subcmd/exec-cmd.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "deferred execution",
    "kernel/workqueue.c",
    "execv_cmd()",
    "execvp()",
    "scheduler-facing transport ownership",
    "collectExeclArgs()",
    "setupPathWithPwd()",
    "make -C zigux phase8-exec-cmd-test",
]

required_phase8_exec_cmd_markers = [
    'test "phase 8 exec-cmd docs keep the deferred execution boundary explicit"',
    'test "phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned"',
    'test "phase 8 exec-cmd evidence still matches the live C helper anchors"',
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.c",
    "kernel/workqueue.c",
    "`execvp()`",
]

required_exec_cmd_helper_markers = [
    "pub const max_execl_slots: usize = 32;",
    "pub fn choosePwdCwdFromIdentities(",
    "pub fn setupPathWithPwd(",
    "pub fn collectExeclArgs(",
    "pub fn buildDeferredExeclCall(",
    'test "buildDeferredExeclCall keeps the execl handoff pure and launch-free"',
    'test "setupPathWithPwd reuses the logical PWD only when the injected identities match"',
]

required_help_slice_markers = [
    "PHASE8_SLICE=help-command-source-and-terminal-starter",
    "tools/lib/subcmd/help.zig",
    "zigux/tests/phase8_help.zig",
    "stable command-list manipulation logic",
    "raw `PATH` string splitting that preserves empty colon-delimited segments",
    "section-level output stays testable",
    "shared longest-name calculation",
    "empty-section suppression",
    "list_commands()",
    "does not yet claim:",
    "cmd_help()",
]

required_phase8_help_markers = [
    'test "phase 8 help docs keep the parked stable-output boundary explicit"',
    'test "phase 8 help review checklist keeps the parked stable-output packet reviewable"',
    'test "phase 8 help evidence still matches the live C helper anchors"',
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/review-checklist.md",
    "tools/lib/subcmd/help.c",
    "`load_command_list()`",
    "`list_commands()`",
]

required_help_helper_markers = [
    "pub fn loadCommandListsFromSource(",
    "pub fn loadCommandListsFromEnvPath(",
    "pub fn splitPathEntries(",
    "pub fn longestNameLenAcrossLists(",
    "pub fn resolveTerminalDimensions(",
    'test "splitPathEntries preserves empty PATH segments and owns copied slices"',
    'test "loadCommandListsFromSource keeps exec-path priority and filters duplicates across PATH"',
    'test "loadCommandListsFromEnvPath preserves raw PATH splitting and exec-path filtering"',
    'test "longestNameLenAcrossLists mirrors list_commands shared column width"',
    'test "writePrettyPrintStringListForTerminal keeps column-major pretty-printing pure and testable"',
    'test "writeCommandSectionsForTerminal keeps list_commands formatting pure and shared-width aware"',
    'test "writeCommandSectionsForTerminal suppresses empty sections without stray headings or blank lines"',
]

required_kallsyms_slice_markers = [
    "PHASE8_SLICE=kallsyms-parse-wrapper-starter",
    "tools/lib/symbol/kallsyms.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "chunked overlong-line handling",
    "stops buffering after the bounded callback surface is full",
    "kallsymsParse()",
    "kallsymsParseInDir()",
    "api/io.h",
]

required_phase8_kallsyms_markers = [
    'test "phase 8 kallsyms docs keep the parked parser boundary explicit"',
    'test "phase 8 kallsyms review checklist keeps the parked parser packet reviewable"',
    'test "phase 8 kallsyms evidence still matches the live C helper anchors"',
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/review-checklist.md",
    "tools/lib/symbol/kallsyms.c",
    "read_to_eol",
    "char symbol_name[KSYM_NAME_LEN + 1];",
]

required_kallsyms_helper_markers = [
    "pub const max_buffered_line_len: usize = 32 + 3 + KSYM_NAME_LEN;",
    "discarding_tail: bool = false,",
    "pub fn forEachParsedChunked(",
    "pub fn kallsymsParseInDir(",
    "pub fn kallsymsParse(",
    'test "forEachParsedChunked discards oversized line tails once the bounded callback surface is full"',
    'test "kallsymsParse wrappers preserve the C-shaped callback contract and bounded names"',
]

required_cpu_mask_markers = [
    "libbpf-cpu-mask-starter",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "parse_cpu_mask_str()",
    "parse_cpu_mask_file()",
    "`libbpf_num_possible_cpus()` caching",
    "`perf_buffer__new()` online CPU selection",
    "interrupt-routing behavior",
    "perf-buffer-online-cpu-routing",
    "per-CPU perf-buffer routing",
]

required_logging_survey_markers = [
    "invalid log-level text stays explicit while callers still receive the default `info` minimum level",
    "the bounded major, minor, and version-string helpers match the current `tools/lib/bpf/libbpf_version.h` tuple",
    "libbpf-specific custom error text stays stable and unmapped custom codes fall back cleanly",
]

required_phase8_logging_markers = [
    'test "phase 8 logging segment keeps libbpf log-level parsing bounded and explicit"',
    'test "phase 8 logging segment reports the bounded libbpf version helpers"',
    'test "phase 8 logging segment keeps libbpf-specific error text stable"',
    'logging.resolveMinPrintLevel("warn")',
    "logging.libbpfVersionString()",
    "logging.libbpfCustomErrorMessage(4007).?",
]

required_logging_helper_markers = [
    'pub const libbpf_log_level_env_var = "LIBBPF_LOG_LEVEL";',
    "pub fn resolveMinPrintLevel(env_value: ?[]const u8) ResolvedMinLevel {",
    "pub fn formatInvalidLogLevelWarning(",
    'test "formatInvalidLogLevelWarning matches libbpf\'s explicit invalid envvar guidance"',
    'test "formatInvalidLogLevelWarning keeps buffer exhaustion explicit"',
]

required_pin_path_survey_markers = [
    "default and caller-provided pin roots join cleanly with map names",
    "`.` characters inside pin roots and map names sanitize to `_` the same way bpffs pin-name helpers do in libbpf",
    "buffer exhaustion during pin-path assembly stays explicit",
]

required_phase8_pin_path_markers = [
    'test "phase 8 pin-path segment keeps map-path joining bounded and explicit"',
    'test "phase 8 pin-path segment sanitizes dots the same way bpffs pin names do"',
    'test "phase 8 pin-path segment keeps validation and path-shape checks bounded"',
    'test "phase 8 pin-path segment keeps overflow failures explicit"',
    'test "phase 8 pin-path segment resolves stored versus requested pin paths"',
    'test "phase 8 pin-path segment resolves stored versus requested unpin paths"',
]

required_pin_path_helper_markers = [
    'pub const default_bpf_fs_path = "/sys/fs/bpf";',
    "pub fn buildValidatedSanitizedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {",
    "pub fn resolveMapPinRequest(",
    "pub fn resolveMapUnpinRequest(",
    'test "pin-path helpers resolve stored and requested map pin paths without widening into syscalls"',
    'test "pin-path helpers resolve stored and requested unpin paths explicitly"',
]

required_phase8_file_path_handle_bridge_markers = [
    'test "phase 8 file-path-handle bridge builds proc fdinfo paths without widening into io"',
    'test "phase 8 file-path-handle bridge keeps the current-process fdinfo helper aligned"',
    'test "phase 8 file-path-handle bridge plans token preparation without claiming live bpffs io"',
    'test "phase 8 file-path-handle bridge keeps token failure recovery discipline explicit"',
    'test "phase 8 file-path-handle bridge mirrors libbpf zero-init and last-field-wins fdinfo fallback"',
    'test "phase 8 file-path-handle bridge keeps the DEVMAP readonly-prog compatibility exception explicit"',
    "buildCurrentProcessFdinfoPath(&actual, 11)",
    "skip_optional_missing_delegation",
    "normalizeReuseCompatibilityMapFlags(expected.map_type, actual.map_flags)",
]

required_file_path_handle_bridge_helper_markers = [
    "pub fn buildCurrentProcessFdinfoPath(buffer: []u8, fd: i32) FilePathHandleBridgeError![]u8 {",
    "pub fn planTokenPreparation(token_path: ?[]const u8) TokenPreparationPlan {",
    "pub fn classifyTokenPreparationFailure(",
    "pub fn chooseReusedMapName(requested_name: []const u8, info_name: []const u8) []const u8 {",
    "pub fn parseMapInfoFromFdinfo(input: []const u8) FilePathHandleBridgeError!FdInfoMapInfo {",
    "pub fn normalizeReuseCompatibilityMapFlags(expected_map_type: u32, actual_map_flags: u32) u32 {",
    "pub fn isMapReuseCompatible(expected: FdInfoMapInfo, actual: FdInfoMapInfo) bool {",
    'test "parseMapInfoFromFdinfo mirrors libbpf\'s zero-init and last-field-wins fallback"',
    'test "normalizeReuseCompatibilityMapFlags mirrors libbpf\'s DEVMAP readonly-prog exception"',
]

required_type_name_markers = [
    "libbpf-type-name-segment",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "make -C zigux phase8",
    "dense attach, link, map, and program type string helpers only",
    "every table entry is reachable through the corresponding helper",
    "representative late enum ordinals from `tools/include/uapi/linux/bpf.h` still resolve to the expected names",
    "deprecated-but-still-addressable map ordinals preserve the shipped libbpf names",
    "out-of-range negative and oversized values are rejected cleanly",
]

required_phase8_bpf_type_names_markers = [
    'test "phase 8 bpf type-name segment keeps live libbpf tables aligned with current UAPI ordinals"',
    'test "phase 8 bpf type-name segment still exposes the current live enum ceilings"',
    "tools/include/uapi/linux/bpf.h",
    "tools/lib/bpf/libbpf.c",
    "static const char * const attach_type_name[] = {",
    "static const char * const link_type_name[] = {",
    "static const char * const map_type_name[] = {",
    "static const char * const prog_type_name[] = {",
    "enum bpf_attach_type {",
    "enum bpf_link_type {",
    "enum bpf_map_type {",
    "enum bpf_prog_type {",
    '"trace_fsession"',
    '"sockmap"',
    '"insn_array"',
    '"netfilter"',
]

required_type_names_helper_markers = [
    "pub const attach_type_names =",
    "pub const link_type_names =",
    "pub const map_type_names =",
    "pub const prog_type_names =",
    "pub fn libbpfBpfAttachTypeStr",
    "pub fn libbpfBpfLinkTypeStr",
    "pub fn libbpfBpfMapTypeStr",
    "pub fn libbpfBpfProgTypeStr",
    'try std.testing.expectEqualStrings("trace_fsession", libbpfBpfAttachTypeStr(58).?);',
    'try std.testing.expectEqualStrings("sockmap", libbpfBpfLinkTypeStr(14).?);',
    'try std.testing.expectEqualStrings("insn_array", libbpfBpfMapTypeStr(34).?);',
    'try std.testing.expectEqualStrings("netfilter", libbpfBpfProgTypeStr(32).?);',
    'test "type-name helpers reject out-of-range values the same way as libbpf.c"',
]

required_manifest_markers = [
    '"slug": "cpu-mask-parsing"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/cpu_mask.zig"',
    '"slug": "logging-version-and-errno"',
    '"status": "starter_landed"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/logging.zig"',
    '"slug": "pin-path-helpers"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/pin_path.zig"',
    '"slug": "fdinfo-map-info-helpers"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
    '"kind": "helper_first"',
    '"tools/lib/bpf/libbpf.c:4956-4987"',
    "path construction",
    "text parsing",
    '"slug": "map-reuse-compatibility"',
    '"tools/lib/bpf/libbpf.c:5220-5251"',
    "DEVMAP readonly-flag exception",
    '"slug": "file-path-and-handle-bridge"',
    '"slug": "file-path-and-handle-bridge",\n      "status": "deferred_high_risk"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
    '"kind": "resource_boundary"',
    '"tools/lib/bpf/libbpf.c:5112-5157"',
    '"tools/lib/bpf/libbpf.c:5255-5286"',
    "token-preparation planner",
    "real bpffs path opens",
    "bpffs path opens",
    "token creation",
    "pinned-object reopen flows",
    "fd ownership",
    '"slug": "type-name-helpers"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/type_names.zig"',
    '"slug": "perf-buffer-online-cpu-routing"',
    '"kind": "interrupt_routing_boundary"',
    '"tools/lib/bpf/libbpf.c:14049-14110"',
    '"tools/lib/bpf/libbpf.c:14429-14480"',
    "online CPU filtering",
    "perf-event-array map updates",
    "interrupt-routing contract",
]


def required_marker_count() -> int:
    return (
        len(required_make_markers)
        + len(required_workflow_markers)
        + len(required_script_readme_markers)
        + len(required_tests_readme_markers)
        + len(required_doc_readme_markers)
        + len(required_review_checklist_markers)
        + len(required_phase8_build_markers)
        + len(required_phase8_exec_cmd_only_build_markers)
        + len(required_phase8_help_only_build_markers)
        + len(required_phase8_kallsyms_only_build_markers)
        + len(required_phase8_libbpf_segments_only_build_markers)
        + len(required_survey_markers)
        + len(required_bridge_boundary_markers)
        + len(required_exec_cmd_slice_markers)
        + len(required_phase8_exec_cmd_markers)
        + len(required_exec_cmd_helper_markers)
        + len(required_help_slice_markers)
        + len(required_phase8_help_markers)
        + len(required_help_helper_markers)
        + len(required_kallsyms_slice_markers)
        + len(required_phase8_kallsyms_markers)
        + len(required_kallsyms_helper_markers)
        + len(required_cpu_mask_markers)
        + len(required_logging_survey_markers)
        + len(required_phase8_logging_markers)
        + len(required_logging_helper_markers)
        + len(required_pin_path_survey_markers)
        + len(required_phase8_pin_path_markers)
        + len(required_pin_path_helper_markers)
        + len(required_phase8_file_path_handle_bridge_markers)
        + len(required_file_path_handle_bridge_helper_markers)
        + len(required_type_name_markers)
        + len(required_phase8_bpf_type_names_markers)
        + len(required_type_names_helper_markers)
        + len(required_manifest_markers)
    )


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    script_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    doc_readme = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    phase8_build = read_text(root, "zigux/tests/phase8_build.zig")
    phase8_exec_cmd_only_build = read_text(root, "zigux/tests/phase8_exec_cmd_only_build.zig")
    phase8_help_only_build = read_text(root, "zigux/tests/phase8_help_only_build.zig")
    phase8_kallsyms_only_build = read_text(root, "zigux/tests/phase8_kallsyms_only_build.zig")
    phase8_libbpf_segments_only_build = read_text(root, "zigux/tests/phase8_libbpf_segments_only_build.zig")
    phase8_survey = read_text(root, "Documentation/zigux/phase8-libbpf-segment-survey.md")
    phase8_bridge_boundary = read_text(root, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md")
    phase8_exec_cmd_slice = read_text(root, "Documentation/zigux/phase8-exec-cmd-slice.md")
    phase8_help_slice = read_text(root, "Documentation/zigux/phase8-help-slice.md")
    phase8_kallsyms_slice = read_text(root, "Documentation/zigux/phase8-kallsyms-slice.md")
    phase8_cpu_mask = read_text(root, "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md")
    phase8_type_names = read_text(root, "Documentation/zigux/phase8-bpf-type-names-slice.md")
    manifest = read_text(root, "tools/lib/bpf/zigux_segments/manifest.json")
    phase8_libbpf_segments_test = read_text(root, "zigux/tests/phase8_libbpf_segments.zig")
    phase8_bpf_type_names_test = read_text(root, "zigux/tests/phase8_bpf_type_names.zig")
    phase8_file_path_handle_bridge_test = read_text(root, "zigux/tests/phase8_file_path_handle_bridge.zig")
    phase8_exec_cmd_test = read_text(root, "zigux/tests/phase8_exec_cmd.zig")
    phase8_help_test = read_text(root, "zigux/tests/phase8_help.zig")
    phase8_kallsyms_test = read_text(root, "zigux/tests/phase8_kallsyms.zig")
    phase8_logging_test = read_text(root, "zigux/tests/phase8_logging.zig")
    phase8_pin_path_test = read_text(root, "zigux/tests/phase8_pin_path.zig")
    exec_cmd_helper = read_text(root, "tools/lib/subcmd/exec-cmd.zig")
    help_helper = read_text(root, "tools/lib/subcmd/help.zig")
    kallsyms_helper = read_text(root, "tools/lib/symbol/kallsyms.zig")
    logging_helper = read_text(root, "tools/lib/bpf/zigux_segments/logging.zig")
    file_path_handle_bridge_helper = read_text(root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig")
    pin_path_helper = read_text(root, "tools/lib/bpf/zigux_segments/pin_path.zig")
    type_names_helper = read_text(root, "tools/lib/bpf/zigux_segments/type_names.zig")

    missing_markers: list[str] = []
    commit_sync_errors: list[str] = []

    for marker in required_make_markers:
        if marker not in makefile:
            missing_markers.append(f"make:{marker}")
    for marker in required_workflow_markers:
        if marker not in workflow:
            missing_markers.append(f"workflow:{marker}")
    for marker in required_script_readme_markers:
        if marker not in script_readme:
            missing_markers.append(f"script_readme:{marker}")
    for marker in required_tests_readme_markers:
        if marker not in tests_readme:
            missing_markers.append(f"tests_readme:{marker}")
    for marker in required_doc_readme_markers:
        if marker not in doc_readme:
            missing_markers.append(f"doc_readme:{marker}")
    for marker in required_review_checklist_markers:
        if marker not in review_checklist:
            missing_markers.append(f"review_checklist:{marker}")
    for marker in required_phase8_build_markers:
        if marker not in phase8_build:
            missing_markers.append(f"phase8_build:{marker}")
    for marker in required_phase8_exec_cmd_only_build_markers:
        if marker not in phase8_exec_cmd_only_build:
            missing_markers.append(f"phase8_exec_cmd_only_build:{marker}")
    for marker in required_phase8_help_only_build_markers:
        if marker not in phase8_help_only_build:
            missing_markers.append(f"phase8_help_only_build:{marker}")
    for marker in required_phase8_kallsyms_only_build_markers:
        if marker not in phase8_kallsyms_only_build:
            missing_markers.append(f"phase8_kallsyms_only_build:{marker}")
    for marker in required_phase8_libbpf_segments_only_build_markers:
        if marker not in phase8_libbpf_segments_only_build:
            missing_markers.append(f"phase8_libbpf_segments_only_build:{marker}")
    for marker in required_survey_markers:
        if marker not in phase8_survey:
            missing_markers.append(f"phase8_survey:{marker}")
    for marker in required_bridge_boundary_markers:
        if marker not in phase8_bridge_boundary:
            missing_markers.append(f"phase8_bridge_boundary:{marker}")
    for marker in required_exec_cmd_slice_markers:
        if marker not in phase8_exec_cmd_slice:
            missing_markers.append(f"phase8_exec_cmd_slice:{marker}")
    for marker in required_phase8_exec_cmd_markers:
        if marker not in phase8_exec_cmd_test:
            missing_markers.append(f"phase8_exec_cmd:{marker}")
    for marker in required_exec_cmd_helper_markers:
        if marker not in exec_cmd_helper:
            missing_markers.append(f"exec_cmd_helper:{marker}")
    for marker in required_help_slice_markers:
        if marker not in phase8_help_slice:
            missing_markers.append(f"phase8_help_slice:{marker}")
    for marker in required_phase8_help_markers:
        if marker not in phase8_help_test:
            missing_markers.append(f"phase8_help:{marker}")
    for marker in required_help_helper_markers:
        if marker not in help_helper:
            missing_markers.append(f"help_helper:{marker}")
    for marker in required_kallsyms_slice_markers:
        if marker not in phase8_kallsyms_slice:
            missing_markers.append(f"phase8_kallsyms_slice:{marker}")
    for marker in required_phase8_kallsyms_markers:
        if marker not in phase8_kallsyms_test:
            missing_markers.append(f"phase8_kallsyms:{marker}")
    for marker in required_kallsyms_helper_markers:
        if marker not in kallsyms_helper:
            missing_markers.append(f"kallsyms_helper:{marker}")
    for marker in required_cpu_mask_markers:
        if marker not in phase8_cpu_mask:
            missing_markers.append(f"phase8_cpu_mask:{marker}")
    for marker in required_logging_survey_markers:
        if marker not in phase8_survey:
            missing_markers.append(f"phase8_survey_logging:{marker}")
    for marker in required_phase8_logging_markers:
        if marker not in phase8_logging_test:
            missing_markers.append(f"phase8_logging:{marker}")
    for marker in required_logging_helper_markers:
        if marker not in logging_helper:
            missing_markers.append(f"logging_helper:{marker}")
    for marker in required_pin_path_survey_markers:
        if marker not in phase8_survey:
            missing_markers.append(f"phase8_survey_pin_path:{marker}")
    for marker in required_phase8_pin_path_markers:
        if marker not in phase8_pin_path_test:
            missing_markers.append(f"phase8_pin_path:{marker}")
    for marker in required_pin_path_helper_markers:
        if marker not in pin_path_helper:
            missing_markers.append(f"pin_path_helper:{marker}")
    for marker in required_phase8_file_path_handle_bridge_markers:
        if marker not in phase8_file_path_handle_bridge_test:
            missing_markers.append(f"phase8_file_path_handle_bridge:{marker}")
    for marker in required_file_path_handle_bridge_helper_markers:
        if marker not in file_path_handle_bridge_helper:
            missing_markers.append(f"file_path_handle_bridge_helper:{marker}")
    for marker in required_type_name_markers:
        if marker not in phase8_type_names:
            missing_markers.append(f"phase8_type_names:{marker}")
    for marker in required_phase8_bpf_type_names_markers:
        if marker not in phase8_bpf_type_names_test:
            missing_markers.append(f"phase8_bpf_type_names:{marker}")
    for marker in required_type_names_helper_markers:
        if marker not in type_names_helper:
            missing_markers.append(f"type_names_helper:{marker}")
    for marker in required_manifest_markers:
        if marker not in manifest:
            missing_markers.append(f"manifest:{marker}")

    try:
        surveyed_commit_from_note = require_match(
            r"survey checkpoint: refreshed against inspected `master` head `([0-9a-f]{40})`",
            phase8_survey,
            "survey_note:missing_or_invalid_surveyed_commit",
        )
        surveyed_commit_from_manifest = require_match(
            r'"surveyed_commit"\s*:\s*"([0-9a-f]{40})"',
            manifest,
            "manifest:missing_or_invalid_surveyed_commit",
        )
        surveyed_commit_from_test = require_match(
            r'const current_surveyed_commit = "([0-9a-f]{40})";',
            phase8_libbpf_segments_test,
            "phase8_libbpf_segments_test:missing_or_invalid_current_surveyed_commit",
        )
    except ValueError as exc:
        commit_sync_errors.append(str(exc))
    else:
        if (
            surveyed_commit_from_note != surveyed_commit_from_manifest
            or surveyed_commit_from_note != surveyed_commit_from_test
        ):
            commit_sync_errors.extend(
                [
                    f"survey_note:{surveyed_commit_from_note}",
                    f"manifest:{surveyed_commit_from_manifest}",
                    f"phase8_libbpf_segments_test:{surveyed_commit_from_test}",
                ]
            )

    return [], missing_markers, commit_sync_errors


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(read_text(ROOT, rel_path), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers, commit_sync_errors = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase8-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if commit_sync_errors:
        raise SystemExit(
            f"phase8-self-test:{label}:unexpected_commit_sync:{','.join(commit_sync_errors)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase8-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers, commit_sync_errors = validate(tmp_root)
        if missing_files or missing_markers or commit_sync_errors:
            raise SystemExit(
                "phase8-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"commit_sync={','.join(commit_sync_errors) if commit_sync_errors else 'none'}"
            )

        survey_path = tmp_root / "Documentation/zigux/phase8-libbpf-segment-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "optional-versus-mandatory bpffs intent",
                "optional-versus-mandatory bpffs",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_marker",
            tmp_root,
            "phase8_survey:optional-versus-mandatory bpffs intent",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "The manifest currently records eleven bounded segments:",
                "The manifest currently records ten bounded segments:",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_segment_count",
            tmp_root,
            "phase8_survey:The manifest currently records eleven bounded segments:",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        help_helper_path = tmp_root / "tools/lib/subcmd/help.zig"
        original_help_helper = help_helper_path.read_text(encoding="utf-8")
        help_helper_path.write_text(
            original_help_helper.replace(
                'test "splitPathEntries preserves empty PATH segments and owns copied slices"',
                'test "splitPathEntries preserves PATH segments"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "help_helper_marker",
            tmp_root,
            'help_helper:test "splitPathEntries preserves empty PATH segments and owns copied slices"',
        )
        help_helper_path.write_text(original_help_helper, encoding="utf-8")

        phase8_build_path = tmp_root / "zigux/tests/phase8_build.zig"
        original_phase8_build = phase8_build_path.read_text(encoding="utf-8")
        phase8_build_path.write_text(
            original_phase8_build.replace(
                '        .name = "phase8-file-path-handle-bridge-tests",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase8_build_artifact_name",
            tmp_root,
            "phase8_build:phase8-file-path-handle-bridge-tests",
        )
        phase8_build_path.write_text(original_phase8_build, encoding="utf-8")

        kallsyms_helper_path = tmp_root / "tools/lib/symbol/kallsyms.zig"
        original_kallsyms_helper = kallsyms_helper_path.read_text(encoding="utf-8")
        kallsyms_helper_path.write_text(
            original_kallsyms_helper.replace(
                'test "forEachParsedChunked discards oversized line tails once the bounded callback surface is full"',
                'test "forEachParsedChunked discards oversized line tails"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "kallsyms_helper_marker",
            tmp_root,
            'kallsyms_helper:test "forEachParsedChunked discards oversized line tails once the bounded callback surface is full"',
        )
        kallsyms_helper_path.write_text(original_kallsyms_helper, encoding="utf-8")

        libbpf_segments_test_path = tmp_root / "zigux/tests/phase8_libbpf_segments.zig"
        original_libbpf_segments_test = libbpf_segments_test_path.read_text(encoding="utf-8")
        libbpf_segments_test_path.write_text(
            original_libbpf_segments_test.replace(
                'const current_surveyed_commit = "',
                'const current_surveyed_commit = "f',
                1,
            ),
            encoding="utf-8",
        )
        missing_files, missing_markers, commit_sync_errors = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase8-self-test:commit_sync_mismatch:unexpected_file_or_marker_failure:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )
        if "phase8_libbpf_segments_test:" not in ",".join(commit_sync_errors):
            actual = ",".join(commit_sync_errors) if commit_sync_errors else "none"
            raise SystemExit(
                "phase8-self-test:commit_sync_mismatch:"
                f"expected_phase8_libbpf_segments_test_marker:actual:{actual}"
            )

    print("PHASE8_VALIDATOR_SELF_TEST=pass")
    print("PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 8 tooling review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in validator drift checks against a temporary Phase 8 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers, commit_sync_errors = validate(ROOT)
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
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE8_MARKERS_END")
        return 1
    if commit_sync_errors:
        print("PHASE8_VALIDATION=fail")
        if len(commit_sync_errors) == 1 and ":missing_or_invalid_" in commit_sync_errors[0]:
            print("MISSING_PHASE8_COMMIT_SYNC_START")
            print(commit_sync_errors[0])
            print("MISSING_PHASE8_COMMIT_SYNC_END")
        else:
            print("MISMATCHED_PHASE8_COMMIT_SYNC_START")
            for item in commit_sync_errors:
                print(item)
            print("MISMATCHED_PHASE8_COMMIT_SYNC_END")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
