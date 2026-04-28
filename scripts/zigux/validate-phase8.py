#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase8.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
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
phase8_build = (ROOT / "zigux" / "tests" / "phase8_build.zig").read_text(encoding="utf-8")
phase8_survey = (ROOT / "Documentation" / "zigux" / "phase8-libbpf-segment-survey.md").read_text(encoding="utf-8")
phase8_bridge_boundary = (ROOT / "Documentation" / "zigux" / "phase8-userspace-kernel-bridge-boundary-survey.md").read_text(encoding="utf-8")
phase8_exec_cmd_slice = (ROOT / "Documentation" / "zigux" / "phase8-exec-cmd-slice.md").read_text(encoding="utf-8")
phase8_cpu_mask = (ROOT / "Documentation" / "zigux" / "phase8-libbpf-cpu-mask-slice.md").read_text(encoding="utf-8")
phase8_type_names = (ROOT / "Documentation" / "zigux" / "phase8-bpf-type-names-slice.md").read_text(encoding="utf-8")
manifest = (ROOT / "tools" / "lib" / "bpf" / "zigux_segments" / "manifest.json").read_text(encoding="utf-8")
phase8_exec_cmd_test = (ROOT / "zigux" / "tests" / "phase8_exec_cmd.zig").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase8-validate phase8-test phase8",
    "phase8-validate:",
    "scripts/zigux/validate-phase8.py",
    "phase8-test:",
    "zigux/tests/phase8_build.zig",
    "phase8: phase8-validate phase8-test",
]

required_workflow_markers = [
    "Validate Phase 8 tooling gates",
    "make -C zigux phase8-validate",
    "Run Phase 8 tooling tests",
    "zigux/tests/phase8_build.zig",
]

required_script_readme_markers = [
    "validate-phase8.py",
    "Phase 8 flow",
    "make -C zigux phase8-validate",
    "phase8_build.zig",
    "phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.zig",
    "deferred execution",
    "execvp()",
    "kernel/workqueue.c",
    "phase8-libbpf-segment-survey.md",
    "cpu_mask.zig",
    "type_names.zig",
]

required_tests_readme_markers = [
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "zigux/tests/phase8_cpu_mask.zig",
    "zigux/tests/phase8_logging.zig",
    "zigux/tests/phase8_pin_path.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "scripts/zigux/validate-phase8.py",
]

required_doc_readme_markers = [
    "Phase 8 notes",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "python3 scripts/zigux/validate-phase8.py",
    "make -C zigux phase8-validate",
    "make -C zigux phase8",
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
    "text parsing",
    "/proc/.../fdinfo",
    "`open()` or `close()` ownership",
    "`bpf_obj_get()` reopen flows",
    "`bpf_token_create()` handle lifecycle parity",
    "bpf_object_prepare_token()",
    "bpf_object__reuse_map()",
    "bpf_get_map_info_from_fdinfo()",
    "online CPU filtering",
    "interrupt-routing-sensitive boundary",
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
    "execvp()",
    "environment reads or writes",
    "opendir()",
    "readdir()",
    "ioctl()",
    "/proc/.../fdinfo",
    "`bpf_obj_get()` reopen flows",
    "`bpf_token_create()` handle lifecycle parity",
    "`open()` or `close()` ownership",
    "python3 scripts/zigux/validate-phase8.py",
    "make -C zigux phase8-validate",
    "zig build test --build-file zigux/tests/phase8_build.zig",
]

required_exec_cmd_slice_markers = [
    "PHASE8_SLICE=exec-cmd-tooling-starter",
    "tools/lib/subcmd/exec-cmd.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "deferred execution",
    "kernel/workqueue.c",
    "execv_cmd()",
    "execvp()",
    "scheduler-facing transport ownership",
    "collectExeclArgs()",
    "setupPathWithPwd()",
]

required_phase8_exec_cmd_markers = [
    'test "phase 8 exec-cmd docs keep the deferred execution boundary explicit"',
    'test "phase 8 exec-cmd evidence still matches the live C helper anchors"',
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.c",
    "kernel/workqueue.c",
    "`execvp()`",
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

required_type_name_markers = [
    "libbpf-type-name-segment",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "make -C zigux phase8",
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
    'path construction',
    'text parsing',
    '"slug": "file-path-and-handle-bridge"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
    '"kind": "resource_boundary"',
    '"tools/lib/bpf/libbpf.c:5112-5157"',
    '"tools/lib/bpf/libbpf.c:5255-5286"',
    'bpffs path opens',
    'token creation',
    'pinned-object reopen flows',
    'fd ownership',
    '"slug": "type-name-helpers"',
    '"zigux_destination": "tools/lib/bpf/zigux_segments/type_names.zig"',
    '"slug": "perf-buffer-online-cpu-routing"',
    '"kind": "interrupt_routing_boundary"',
    '"tools/lib/bpf/libbpf.c:14049-14110"',
    '"tools/lib/bpf/libbpf.c:14429-14480"',
    'online CPU filtering',
    'perf-event-array map updates',
    'interrupt-routing contract',
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
for marker in required_phase8_build_markers:
    if marker not in phase8_build:
        missing_markers.append(f"phase8_build:{marker}")
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
for marker in required_cpu_mask_markers:
    if marker not in phase8_cpu_mask:
        missing_markers.append(f"phase8_cpu_mask:{marker}")
for marker in required_type_name_markers:
    if marker not in phase8_type_names:
        missing_markers.append(f"phase8_type_names:{marker}")
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

print("PHASE8_VALIDATION=pass")
print(f"PHASE8_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE8_REQUIRED_MARKER_COUNT="
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_phase8_build_markers) + len(required_survey_markers) + len(required_bridge_boundary_markers) + len(required_exec_cmd_slice_markers) + len(required_phase8_exec_cmd_markers) + len(required_cpu_mask_markers) + len(required_type_name_markers) + len(required_manifest_markers)}"
)