#!/usr/bin/env python3
import re
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase8.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "phase8-exec-cmd-slice.md",
    ROOT / "Documentation" / "zigux" / "phase8-help-slice.md",
    ROOT / "Documentation" / "zigux" / "phase8-kallsyms-slice.md",
    ROOT / "Documentation" / "zigux" / "phase8-libbpf-cpu-mask-slice.md",
    ROOT / "Documentation" / "zigux" / "phase8-bpf-type-names-slice.md",
    ROOT / "Documentation" / "zigux" / "phase8-libbpf-segment-survey.md",
    ROOT / "Documentation" / "zigux" / "phase8-userspace-kernel-bridge-boundary-survey.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase8_build.zig",
    ROOT / "zigux" / "tests" / "phase8_exec_cmd_only_build.zig",
    ROOT / "zigux" / "tests" / "phase8_help_only_build.zig",
    ROOT / "zigux" / "tests" / "phase8_kallsyms_only_build.zig",
    ROOT / "zigux" / "tests" / "phase8_libbpf_segments_only_build.zig",
    ROOT / "zigux" / "tests" / "phase8_exec_cmd.zig",
    ROOT / "zigux" / "tests" / "phase8_help.zig",
    ROOT / "zigux" / "tests" / "phase8_kallsyms.zig",
    ROOT / "zigux" / "tests" / "phase8_cpu_mask.zig",
    ROOT / "zigux" / "tests" / "phase8_logging.zig",
    ROOT / "zigux" / "tests" / "phase8_pin_path.zig",
    ROOT / "zigux" / "tests" / "phase8_file_path_handle_bridge.zig",
    ROOT / "zigux" / "tests" / "phase8_libbpf_segments.zig",
    ROOT / "zigux" / "tests" / "phase8_bpf_type_names.zig",
    ROOT / "tools" / "lib" / "subcmd" / "exec-cmd.zig",
    ROOT / "tools" / "lib" / "subcmd" / "help.zig",
    ROOT / "tools" / "lib" / "symbol" / "kallsyms.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "cpu_mask.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "logging.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "pin_path.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "file_path_handle_bridge.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "type_names.zig",
    ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "manifest.json",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE8_VALIDATION=fail")
    print("MISSING_PHASE8_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE8_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
phase8_build = (ROOT / "zigux" / "tests" / "phase8_build.zig").read_text(encoding="utf-8")
phase8_exec_cmd_only_build = (ROOT / "zigux" / "tests" / "phase8_exec_cmd_only_build.zig").read_text(encoding="utf-8")
phase8_help_only_build = (ROOT / "zigux" / "tests" / "phase8_help_only_build.zig").read_text(encoding="utf-8")
phase8_kallsyms_only_build = (ROOT / "zigux" / "tests" / "phase8_kallsyms_only_build.zig").read_text(encoding="utf-8")
phase8_libbpf_segments_only_build = (ROOT / "zigux" / "tests" / "phase8_libbpf_segments_only_build.zig").read_text(encoding="utf-8")
phase8_survey = (ROOT / "Documentation" / "zigux" / "phase8-libbpf-segment-survey.md").read_text(encoding="utf-8")
phase8_bridge_boundary = (ROOT / "Documentation" / "zigux" / "phase8-userspace-kernel-bridge-boundary-survey.md").read_text(encoding="utf-8")
phase8_exec_cmd_slice = (ROOT / "Documentation" / "zigux" / "phase8-exec-cmd-slice.md").read_text(encoding="utf-8")
phase8_help_slice = (ROOT / "Documentation" / "zigux" / "phase8-help-slice.md").read_text(encoding="utf-8")
phase8_kallsyms_slice = (ROOT / "Documentation" / "zigux" / "phase8-kallsyms-slice.md").read_text(encoding="utf-8")
phase8_cpu_mask = (ROOT / "Documentation" / "zigux" / "phase8-libbpf-cpu-mask-slice.md").read_text(encoding="utf-8")
phase8_type_names = (ROOT / "Documentation" / "zigux" / "phase8-bpf-type-names-slice.md").read_text(encoding="utf-8")
manifest = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "manifest.json").read_text(encoding="utf-8")
phase8_libbpf_segments_test = (ROOT / "zigux" / "tests" / "phase8_libbpf_segments.zig").read_text(encoding="utf-8")
phase8_bpf_type_names_test = (ROOT / "zigux" / "tests" / "phase8_bpf_type_names.zig").read_text(encoding="utf-8")
phase8_file_path_handle_bridge_test = (ROOT / "zigux" / "tests" / "phase8_file_path_handle_bridge.zig").read_text(encoding="utf-8")
phase8_exec_cmd_test = (ROOT / "zigux" / "tests" / "phase8_exec_cmd.zig").read_text(encoding="utf-8")
phase8_help_test = (ROOT / "zigux" / "tests" / "phase8_help.zig").read_text(encoding="utf-8")
phase8_kallsyms_test = (ROOT / "zigux" / "tests" / "phase8_kallsyms.zig").read_text(encoding="utf-8")
phase8_logging_test = (ROOT / "zigux" / "tests" / "phase8_logging.zig").read_text(encoding="utf-8")
phase8_pin_path_test = (ROOT / "zigux" / "tests" / "phase8_pin_path.zig").read_text(encoding="utf-8")
logging_helper = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "logging.zig").read_text(encoding="utf-8")
file_path_handle_bridge_helper = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "file_path_handle_bridge.zig").read_text(encoding="utf-8")
pin_path_helper = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "pin_path.zig").read_text(encoding="utf-8")
type_names_helper = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "type_names.zig").read_text(encoding="utf-8")


def require_match(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_COMMIT_SYNC_START")
        print(label)
        print("MISSING_PHASE8_COMMIT_SYNC_END")
        sys.exit(1)
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
    "phase8_logging.zig",
    "phase8_pin_path.zig",
    "phase8_file_path_handle_bridge.zig",
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
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "fdinfo-map-info-helpers",
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "phase8_file_path_handle_bridge.zig",
    "path construction",
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
    "test \"phase 8 exec-cmd docs keep the deferred execution boundary explicit\"",
    "test \"phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned\"",
    "test \"phase 8 exec-cmd evidence still matches the live C helper anchors\"",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.c",
    "kernel/workqueue.c",
    "`execvp()`",
]

required_help_slice_markers = [
    "PHASE8_SLICE=help-command-source-and-terminal-starter",
    "tools/lib/subcmd/help.zig",
    "zigux/tests/phase8_help.zig",
    "stable command-list manipulation logic",
    "section-level output stays testable",
    "list_commands()",
    "does not yet claim:",
    "cmd_help()",
]

required_phase8_help_markers = [
    "test \"phase 8 help docs keep the parked stable-output boundary explicit\"",
    "test \"phase 8 help review checklist keeps the parked stable-output packet reviewable\"",
    "test \"phase 8 help evidence still matches the live C helper anchors\"",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/review-checklist.md",
    "tools/lib/subcmd/help.c",
    "`load_command_list()`",
    "`list_commands()`",
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
    "test \"phase 8 kallsyms docs keep the parked parser boundary explicit\"",
    "test \"phase 8 kallsyms review checklist keeps the parked parser packet reviewable\"",
    "test \"phase 8 kallsyms evidence still matches the live C helper anchors\"",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/review-checklist.md",
    "tools/lib/symbol/kallsyms.c",
    "read_to_eol",
    "char symbol_name[KSYM_NAME_LEN + 1];",
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
    "test \"phase 8 logging segment keeps libbpf log-level parsing bounded and explicit\"",
    "test \"phase 8 logging segment reports the bounded libbpf version helpers\"",
    "test \"phase 8 logging segment keeps libbpf-specific error text stable\"",
    "logging.resolveMinPrintLevel(\"warn\")",
    "logging.libbpfVersionString()",
    "logging.libbpfCustomErrorMessage(4007).?",
]

required_logging_helper_markers = [
    "pub const libbpf_log_level_env_var = \"LIBBPF_LOG_LEVEL\";",
    "pub fn resolveMinPrintLevel(env_value: ?[]const u8) ResolvedMinLevel {",
    "pub fn formatInvalidLogLevelWarning(",
    "test \"formatInvalidLogLevelWarning matches libbpf's explicit invalid envvar guidance\"",
    "test \"formatInvalidLogLevelWarning keeps buffer exhaustion explicit\"",
]

required_pin_path_survey_markers = [
    "default and caller-provided pin roots join cleanly with map names",
    "`.` characters inside pin roots and map names sanitize to `_` the same way bpffs pin-name helpers do in libbpf",
    "buffer exhaustion during pin-path assembly stays explicit",
]

required_phase8_pin_path_markers = [
    "test \"phase 8 pin-path segment keeps map-path joining bounded and explicit\"",
    "test \"phase 8 pin-path segment sanitizes dots the same way bpffs pin names do\"",
    "test \"phase 8 pin-path segment keeps validation and path-shape checks bounded\"",
    "test \"phase 8 pin-path segment keeps overflow failures explicit\"",
    "test \"phase 8 pin-path segment resolves stored versus requested pin paths\"",
    "test \"phase 8 pin-path segment resolves stored versus requested unpin paths\"",
]

required_pin_path_helper_markers = [
    "pub const default_bpf_fs_path = \"/sys/fs/bpf\";",
    "pub fn buildValidatedSanitizedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {",
    "pub fn resolveMapPinRequest(",
    "pub fn resolveMapUnpinRequest(",
    "test \"pin-path helpers resolve stored and requested map pin paths without widening into syscalls\"",
    "test \"pin-path helpers resolve stored and requested unpin paths explicitly\"",
]

required_phase8_file_path_handle_bridge_markers = [
    "test \"phase 8 file-path-handle bridge builds proc fdinfo paths without widening into io\"",
    "test \"phase 8 file-path-handle bridge keeps the current-process fdinfo helper aligned\"",
    "test \"phase 8 file-path-handle bridge plans token preparation without claiming live bpffs io\"",
    "test \"phase 8 file-path-handle bridge keeps token failure recovery discipline explicit\"",
    "test \"phase 8 file-path-handle bridge mirrors libbpf zero-init and last-field-wins fdinfo fallback\"",
    "test \"phase 8 file-path-handle bridge keeps the DEVMAP readonly-prog compatibility exception explicit\"",
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
    "test \"parseMapInfoFromFdinfo mirrors libbpf's zero-init and last-field-wins fallback\"",
    "test \"normalizeReuseCompatibilityMapFlags mirrors libbpf's DEVMAP readonly-prog exception\"",
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
    "test \"phase 8 bpf type-name segment keeps live libbpf tables aligned with current UAPI ordinals\"",
    "test \"phase 8 bpf type-name segment still exposes the current live enum ceilings\"",
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
    "\"trace_fsession\"",
    "\"sockmap\"",
    "\"insn_array\"",
    "\"netfilter\"",
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
    "try std.testing.expectEqualStrings(\"trace_fsession\", libbpfBpfAttachTypeStr(58).?);",
    "try std.testing.expectEqualStrings(\"sockmap\", libbpfBpfLinkTypeStr(14).?);",
    "try std.testing.expectEqualStrings(\"insn_array\", libbpfBpfMapTypeStr(34).?);",
    "try std.testing.expectEqualStrings(\"netfilter\", libbpfBpfProgTypeStr(32).?);",
    "test \"type-name helpers reject out-of-range values the same way as libbpf.c\"",
]

required_manifest_markers = [
    "\"slug\": \"cpu-mask-parsing\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/cpu_mask.zig\"",
    "\"slug\": \"logging-version-and-errno\"",
    "\"status\": \"starter_landed\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/logging.zig\"",
    "\"slug\": \"pin-path-helpers\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/pin_path.zig\"",
    "\"slug\": \"fdinfo-map-info-helpers\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
    "\"kind\": \"helper_first\"",
    "\"tools/lib/bpf/libbpf.c:4956-4987\"",
    "path construction",
    "text parsing",
    "\"slug\": \"file-path-and-handle-bridge\"",
    "\"slug\": \"file-path-and-handle-bridge\",\n      \"status\": \"deferred_high_risk\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
    "\"kind\": \"resource_boundary\"",
    "\"tools/lib/bpf/libbpf.c:5112-5157\"",
    "\"tools/lib/bpf/libbpf.c:5255-5286\"",
    "token-preparation planner",
    "real bpffs path opens",
    "bpffs path opens",
    "token creation",
    "pinned-object reopen flows",
    "fd ownership",
    "\"slug\": \"type-name-helpers\"",
    "\"zigux_destination\": \"tools/lib/bpf/zigux_segments/type_names.zig\"",
    "\"slug\": \"perf-buffer-online-cpu-routing\"",
    "\"kind\": \"interrupt_routing_boundary\"",
    "\"tools/lib/bpf/libbpf.c:14049-14110\"",
    "\"tools/lib/bpf/libbpf.c:14429-14480\"",
    "online CPU filtering",
    "perf-event-array map updates",
    "interrupt-routing contract",
]

missing_markers = []

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
for marker in required_help_slice_markers:
    if marker not in phase8_help_slice:
        missing_markers.append(f"phase8_help_slice:{marker}")
for marker in required_phase8_help_markers:
    if marker not in phase8_help_test:
        missing_markers.append(f"phase8_help:{marker}")
for marker in required_kallsyms_slice_markers:
    if marker not in phase8_kallsyms_slice:
        missing_markers.append(f"phase8_kallsyms_slice:{marker}")
for marker in required_phase8_kallsyms_markers:
    if marker not in phase8_kallsyms_test:
        missing_markers.append(f"phase8_kallsyms:{marker}")
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

if missing_markers:
    print("PHASE8_VALIDATION=fail")
    print("MISSING_PHASE8_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE8_MARKERS_END")
    sys.exit(1)

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

if (
    surveyed_commit_from_note != surveyed_commit_from_manifest
    or surveyed_commit_from_note != surveyed_commit_from_test
):
    print("PHASE8_VALIDATION=fail")
    print("MISMATCHED_PHASE8_COMMIT_SYNC_START")
    print(f"survey_note:{surveyed_commit_from_note}")
    print(f"manifest:{surveyed_commit_from_manifest}")
    print(f"phase8_libbpf_segments_test:{surveyed_commit_from_test}")
    print("MISMATCHED_PHASE8_COMMIT_SYNC_END")
    sys.exit(1)

print("PHASE8_VALIDATION=pass")
print(f"PHASE8_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE8_REQUIRED_MARKER_COUNT="
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_review_checklist_markers) + len(required_phase8_build_markers) + len(required_phase8_exec_cmd_only_build_markers) + len(required_phase8_help_only_build_markers) + len(required_phase8_kallsyms_only_build_markers) + len(required_phase8_libbpf_segments_only_build_markers) + len(required_survey_markers) + len(required_bridge_boundary_markers) + len(required_exec_cmd_slice_markers) + len(required_phase8_exec_cmd_markers) + len(required_help_slice_markers) + len(required_phase8_help_markers) + len(required_kallsyms_slice_markers) + len(required_phase8_kallsyms_markers) + len(required_cpu_mask_markers) + len(required_logging_survey_markers) + len(required_phase8_logging_markers) + len(required_logging_helper_markers) + len(required_pin_path_survey_markers) + len(required_phase8_pin_path_markers) + len(required_pin_path_helper_markers) + len(required_phase8_file_path_handle_bridge_markers) + len(required_file_path_handle_bridge_helper_markers) + len(required_type_name_markers) + len(required_phase8_bpf_type_names_markers) + len(required_type_names_helper_markers) + len(required_manifest_markers)}"
)
