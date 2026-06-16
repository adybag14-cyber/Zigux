const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_EXPORT_UAPI_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-export-uapi-boundary-survey_md = [_][]const u8{
    "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_EXPORT_SHIM_INTEROP_POLICY_RELAY=zigux/kernel/export_shim.zig -> validateInteropPolicy",
    "PHASE3_EXPORT_SHIM_RBTREE_RELAY=zigux/kernel/export_shim.zig -> validateRbtreeRootView",
    "PHASE3_ABI_H_PATH=include/zigux/abi.h",
    "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
    "PHASE3_BINDING_HEADER_FAMILY_PATH=zigux/bindings/header_family.zig",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
    "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig",
    "PHASE3_EXPORT_SHIM_BUILD_PATH=zigux/tests/phase3_export_shim_build.zig",
    "PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "PHASE3_C_HEADER_SMOKE_WORKFLOW_ROUTE=.github/workflows/zigux-bootstrap.yml",
    "PHASE3_C_HEADER_SMOKE_WORKFLOW_GATE=.github/workflows/zigux-bootstrap.yml -> Run current Phase 3 export/UAPI C header smoke",
    "PHASE3_ABI_EXPORT_SHARED_GATE=zig build phase3-abi-export --build-file zigux/tests/build.zig",
    "PHASE3_ABI_EXPORT_MAKE_ROUTE=make -C zigux phase3-abi-export",
    "PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage beyond the landed starter packet and focused runtime relays remain open",
    "Do not use this lane to claim broader Phase 3 completion.",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-export-uapi-survey_py = [_][]const u8{
    "\"\"\"Validate the current bounded Phase 3 export/UAPI survey packet.\"\"\"",
    "WORKFLOW_PATH = Path(\".github/workflows/zigux-bootstrap.yml\")",
    "CATALOG_SELFTEST_CHECK_PATH = Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "print(\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass\")",
    "print(\"PHASE3_EXPORT_UAPI_SURVEY=pass\")",
};

const REQUIRED_MARKERS__zigux_kernel_export_shim_zig = [_][]const u8{
    "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
    "pub fn validateVersion(candidate: Version) ExportStatus {",
    "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    "pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {",
    "pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {",
};

const REQUIRED_MARKERS__include_zigux_abi_h = [_][]const u8{
    "#define ZIGUX_ABI_VERSION 1U",
    "typedef struct zigux_boundary_header {",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
    "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
};

const REQUIRED_MARKERS__include_linux_zigux_h = [_][]const u8{
    "static inline struct zigux_export_status zigux_uapi_validate_boundary_header(",
    "static inline struct zigux_export_status zigux_validate_boundary_header(",
    "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
};

const REQUIRED_MARKERS__zigux_bindings_version_zig = [_][]const u8{
    "pub fn current() Version {",
    "pub fn validate(version: Version) ExportStatus {",
};

const REQUIRED_MARKERS__zigux_bindings_dev_t_zig = [_][]const u8{
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const REQUIRED_MARKERS__zigux_bindings_header_family_zig = [_][]const u8{
    "pub const abi_major: u32 = uapi_version.abi_major;",
    "pub fn validateVersionStatus(version: Version) ExportStatus {",
    "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
};

const REQUIRED_MARKERS__zigux_uapi_version_zig = [_][]const u8{
    "pub fn matchesCurrent(version: Version) bool {",
    "pub fn validate(version: Version) abi.ExportStatus {",
};

const REQUIRED_MARKERS__zigux_uapi_dev_t_zig = [_][]const u8{
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const REQUIRED_MARKERS__include_zigux_dev_t_h = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "struct zigux_dev_t_fields {",
    "static inline int zigux_dev_t_fields_range_is_valid(",
};

const REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml = [_][]const u8{
    "- name: Run current Phase 3 export/UAPI C header smoke",
    "run: zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json = [_][]const u8{
    "\"Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\"",
    "\"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig\"",
    "\"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig\"",
    "\"make -C zigux phase3-export-uapi-layout-test\"",
    "\"make -C zigux phase3-export-shim-test\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
    "\"zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\"",
};

const REQUIRED_MARKERS__zigux_tests_build_zig = [_][]const u8{
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
    "const phase3_abi_export_step = b.step(",
    "\"phase3-abi-export\"",
    "phase3_abi_export_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_abi_export_step.dependOn(&phase3_export_shim.step);",
    "phase3_abi_export_step.dependOn(&phase3_export_uapi_layout.step);",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "root_module.addImport(\"export_shim\", export_shim);",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-abi-export:",
    "$(ZIG_REPO_ROOT) build phase3-abi-export --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout:",
    "phase3-export-uapi-layout-test:",
    "phase3-export-shim-test:",
};

const REQUIRED_MARKERS__zigux_tests_phase3_export_shim_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "export_shim_module.addImport(\"version_binding\", version_binding_module);",
    "\"phase3-export-shim-test\",",
};

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_zig = [_][]const u8{
    "test \"header-family binding keeps the bounded relay surface explicit\" {",
    "test \"header-family status wrappers stay aligned with export shim validation\" {",
    "test \"version binding relays centralized boundary header helpers without widening the boundary\" {",
    "test \"export shim relays version compatibility without widening the boundary\" {",
    "test \"export shim relays starter boundary-header validation through the focused replay\" {",
    "test \"export shim relays starter dev_t validation and range checks through the focused replay\" {",
    "test \"export shim reuses the canonical boundary header contract\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "\"phase3-export-uapi-layout-test\",",
};

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_c_header_smoke_c = [_][]const u8{
    "#include <linux/zigux.h>",
    "static int check_boundary_header_relays(void)",
    "zigux_validate_boundary_header(",
    "static int check_dev_t_relays(void)",
    "zigux_uapi_validate_dev_t_range(",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py = [_][]const u8{
    "\"\"\"Compile and run the current Phase 3 export/UAPI C header smoke.\"\"\"",
    "SMOKE_PATH = Path(\"zigux/tests/phase3_export_uapi_c_header_smoke.c\")",
    "print(\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass\")",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-dev-t-starter-packet_py = [_][]const u8{
    "print(\"PHASE3_DEV_T_STARTER_PACKET=pass\")",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-catalog-selftest_py = [_][]const u8{
    "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const REQUIRED_MARKERS__scripts_zigux_validate_phase3_selftest_py = [_][]const u8{
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass\"",
    "\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=\"",
    "Path(\"scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\")",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass\"",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=\"",
    "print(\"PHASE3_VALIDATE_SELFTEST=pass\")",
};

const REQUIRED_MARKERS__scripts_zigux_run-phase3-checks_py = [_][]const u8{
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "\"validated Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"PHASE3_EXPORT_UAPI_SURVEY=pass\"",
    "Path(\"scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\")",
    "\"validated zigux/tests/phase3_export_uapi_c_header_smoke.c\"",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-export-uapi-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-export-uapi-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-export-uapi-survey/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-export-uapi-survey_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py, marker);
    const text_required_markers__zigux_kernel_export_shim_zig_path = try guard.joinPath(allocator, root, "zigux/kernel/export/shim/zig");
    defer allocator.free(text_required_markers__zigux_kernel_export_shim_zig_path);
    const text_required_markers__zigux_kernel_export_shim_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_kernel_export_shim_zig_path);
    defer allocator.free(text_required_markers__zigux_kernel_export_shim_zig);
    for (REQUIRED_MARKERS__zigux_kernel_export_shim_zig) |marker| try guard.requireMarker(text_required_markers__zigux_kernel_export_shim_zig, marker);
    const text_required_markers__include_zigux_abi_h_path = try guard.joinPath(allocator, root, "include/zigux/abi/h");
    defer allocator.free(text_required_markers__include_zigux_abi_h_path);
    const text_required_markers__include_zigux_abi_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_abi_h_path);
    defer allocator.free(text_required_markers__include_zigux_abi_h);
    for (REQUIRED_MARKERS__include_zigux_abi_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_abi_h, marker);
    const text_required_markers__include_linux_zigux_h_path = try guard.joinPath(allocator, root, "include/linux/zigux/h");
    defer allocator.free(text_required_markers__include_linux_zigux_h_path);
    const text_required_markers__include_linux_zigux_h = try guard.readUtf8File(io, allocator, text_required_markers__include_linux_zigux_h_path);
    defer allocator.free(text_required_markers__include_linux_zigux_h);
    for (REQUIRED_MARKERS__include_linux_zigux_h) |marker| try guard.requireMarker(text_required_markers__include_linux_zigux_h, marker);
    const text_required_markers__zigux_bindings_version_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/version/zig");
    defer allocator.free(text_required_markers__zigux_bindings_version_zig_path);
    const text_required_markers__zigux_bindings_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_version_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_version_zig);
    for (REQUIRED_MARKERS__zigux_bindings_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_version_zig, marker);
    const text_required_markers__zigux_bindings_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig_path);
    const text_required_markers__zigux_bindings_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_bindings_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_dev_t_zig, marker);
    const text_required_markers__zigux_bindings_header_family_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/header/family/zig");
    defer allocator.free(text_required_markers__zigux_bindings_header_family_zig_path);
    const text_required_markers__zigux_bindings_header_family_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_header_family_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_header_family_zig);
    for (REQUIRED_MARKERS__zigux_bindings_header_family_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_header_family_zig, marker);
    const text_required_markers__zigux_uapi_version_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/version/zig");
    defer allocator.free(text_required_markers__zigux_uapi_version_zig_path);
    const text_required_markers__zigux_uapi_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_version_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_version_zig);
    for (REQUIRED_MARKERS__zigux_uapi_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_version_zig, marker);
    const text_required_markers__zigux_uapi_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig_path);
    const text_required_markers__zigux_uapi_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_uapi_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_dev_t_zig, marker);
    const text_required_markers__include_zigux_dev_t_h_path = try guard.joinPath(allocator, root, "include/zigux/dev/t/h");
    defer allocator.free(text_required_markers__include_zigux_dev_t_h_path);
    const text_required_markers__include_zigux_dev_t_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_dev_t_h_path);
    defer allocator.free(text_required_markers__include_zigux_dev_t_h);
    for (REQUIRED_MARKERS__include_zigux_dev_t_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_dev_t_h, marker);
    const text_required_markers___github_workflows_zigux-bootstrap_yml_path = try guard.joinPath(allocator, root, "/github/workflows/zigux-bootstrap/yml");
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    const text_required_markers___github_workflows_zigux-bootstrap_yml = try guard.readUtf8File(io, allocator, text_required_markers___github_workflows_zigux-bootstrap_yml_path);
    defer allocator.free(text_required_markers___github_workflows_zigux-bootstrap_yml);
    for (REQUIRED_MARKERS___github_workflows_zigux-bootstrap_yml) |marker| try guard.requireMarker(text_required_markers___github_workflows_zigux-bootstrap_yml, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/abi/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json, marker);
    const text_required_markers__zigux_tests_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_build_zig_path);
    const text_required_markers__zigux_tests_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_build_zig, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_phase3_export_shim_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/shim/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_shim_build_zig_path);
    const text_required_markers__zigux_tests_phase3_export_shim_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_shim_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_shim_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_shim_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_shim_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/layout/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig, marker);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/layout/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/c/header/smoke/c");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_c_header_smoke_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c, marker);
    const text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-export-uapi-c-header-smoke/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py_path);
    const text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-export-uapi-c-header-smoke_py, marker);
    const text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-dev-t-starter-packet/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-dev-t-starter-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-dev-t-starter-packet_py, marker);
    const text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-catalog-selftest/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py_path);
    const text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-catalog-selftest_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-catalog-selftest_py, marker);
    const text_required_markers__scripts_zigux_validate_phase3_selftest_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate/phase3/selftest/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate_phase3_selftest_py_path);
    const text_required_markers__scripts_zigux_validate_phase3_selftest_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate_phase3_selftest_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate_phase3_selftest_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate_phase3_selftest_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate_phase3_selftest_py, marker);
    const text_required_markers__scripts_zigux_run-phase3-checks_py_path = try guard.joinPath(allocator, root, "scripts/zigux/run-phase3-checks/py");
    defer allocator.free(text_required_markers__scripts_zigux_run-phase3-checks_py_path);
    const text_required_markers__scripts_zigux_run-phase3-checks_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_run-phase3-checks_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_run-phase3-checks_py);
    for (REQUIRED_MARKERS__scripts_zigux_run-phase3-checks_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_run-phase3-checks_py, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
