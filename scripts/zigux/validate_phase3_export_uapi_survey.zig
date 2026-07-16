const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_EXPORT_UAPI_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
    "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "validated Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "PHASE3_EXPORT_UAPI_SURVEY=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
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

const markers_1 = [_][]const u8{
    "Validate the current bounded Phase 3 export/UAPI survey packet.",
    ".github/workflows/zigux-bootstrap.yml",
    "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
    "PHASE3_EXPORT_UAPI_SURVEY=pass",
};

const markers_2 = [_][]const u8{
    "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
    "pub fn validateVersion(candidate: Version) ExportStatus {",
    "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    "pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {",
    "pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {",
};

const markers_3 = [_][]const u8{
    "#define ZIGUX_ABI_VERSION 1U",
    "typedef struct zigux_boundary_header {",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
    "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
};

const markers_4 = [_][]const u8{
    "static inline struct zigux_export_status zigux_uapi_validate_boundary_header(",
    "static inline struct zigux_export_status zigux_validate_boundary_header(",
    "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(",
};

const markers_5 = [_][]const u8{
    "pub fn current() Version {",
    "pub fn validate(version: Version) ExportStatus {",
};

const markers_6 = [_][]const u8{
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const markers_7 = [_][]const u8{
    "pub const abi_major: u32 = uapi_version.abi_major;",
    "pub fn validateVersionStatus(version: Version) ExportStatus {",
    "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
};

const markers_8 = [_][]const u8{
    "pub fn matchesCurrent(version: Version) bool {",
    "pub fn validate(version: Version) abi.ExportStatus {",
};

const markers_9 = [_][]const u8{
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const markers_10 = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "struct zigux_dev_t_fields {",
    "static inline int zigux_dev_t_fields_range_is_valid(",
};

const markers_11 = [_][]const u8{
    "- name: Run current Phase 3 export/UAPI C header smoke",
};

const markers_12 = [_][]const u8{
    "\"Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"scripts/zigux/validate_phase3_export_uapi_survey.zig\"",
    "\"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig\"",
    "\"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig\"",
    "\"make -C zigux phase3-export-uapi-layout-test\"",
    "\"make -C zigux phase3-export-shim-test\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
};

const markers_13 = [_][]const u8{
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
    "const phase3_abi_export_step = b.step(",
    "\"phase3-abi-export\"",
    "phase3_abi_export_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_abi_export_step.dependOn(&phase3_export_shim.step);",
    "phase3_abi_export_step.dependOn(&phase3_export_uapi_layout.step);",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "root_module.addImport(\"export_shim\", export_shim);",
};

const markers_14 = [_][]const u8{
    "phase3-abi-export:",
    "$(ZIG_REPO_ROOT) build phase3-abi-export --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout:",
    "phase3-export-uapi-layout-test:",
    "phase3-export-shim-test:",
};

const markers_15 = [_][]const u8{
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "export_shim_module.addImport(\"version_binding\", version_binding_module);",
    "\"phase3-export-shim-test\",",
};

const markers_16 = [_][]const u8{
    "test \"header-family binding keeps the bounded relay surface explicit\" {",
    "test \"header-family status wrappers stay aligned with export shim validation\" {",
    "test \"version binding relays centralized boundary header helpers without widening the boundary\" {",
    "test \"export shim relays version compatibility without widening the boundary\" {",
    "test \"export shim relays starter boundary-header validation through the focused replay\" {",
    "test \"export shim relays starter dev_t validation and range checks through the focused replay\" {",
    "test \"export shim reuses the canonical boundary header contract\" {",
};

const markers_17 = [_][]const u8{
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "\"phase3-export-uapi-layout-test\",",
};

const markers_18 = [_][]const u8{
    "#include <linux/zigux.h>",
    "static int check_boundary_header_relays(void)",
    "zigux_validate_boundary_header(",
    "static int check_dev_t_relays(void)",
    "zigux_uapi_validate_dev_t_range(",
};

const markers_19 = [_][]const u8{
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass",
};

const markers_20 = [_][]const u8{
    "PHASE3_DEV_T_STARTER_PACKET=pass",
};

const markers_21 = [_][]const u8{
    "PHASE3_CATALOG_SELFTEST_CHECK=pass",
    "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass",
};

const markers_22 = [_][]const u8{
    "scripts/zigux/validate_phase3_export_uapi_survey.zig",
    "\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass\"",
    "\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=\"",
    "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass\"",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=\"",
    "PHASE3_VALIDATE_SELFTEST=pass",
};

const markers_23 = [_][]const u8{
    "scripts/zigux/validate_phase3_export_uapi_survey.zig",
    "\"validated Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"PHASE3_EXPORT_UAPI_SURVEY=pass\"",
    "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "\"validated zigux/tests/phase3_export_uapi_c_header_smoke.c\"",
    "\"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-export-uapi-boundary-survey.md", .markers = &markers_0 },
    .{ .rel = "scripts/zigux/validate_phase3_export_uapi_survey.zig", .markers = &markers_1 },
    .{ .rel = "zigux/kernel/export_shim.zig", .markers = &markers_2 },
    .{ .rel = "include/zigux/abi.h", .markers = &markers_3 },
    .{ .rel = "include/linux/zigux.h", .markers = &markers_4 },
    .{ .rel = "zigux/bindings/version.zig", .markers = &markers_5 },
    .{ .rel = "zigux/bindings/dev_t.zig", .markers = &markers_6 },
    .{ .rel = "zigux/bindings/header_family.zig", .markers = &markers_7 },
    .{ .rel = "zigux/uapi/version.zig", .markers = &markers_8 },
    .{ .rel = "zigux/uapi/dev_t.zig", .markers = &markers_9 },
    .{ .rel = "include/zigux/dev_t.h", .markers = &markers_10 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_11 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_12 },
    .{ .rel = "zigux/tests/build.zig", .markers = &markers_13 },
    .{ .rel = "zigux/Makefile", .markers = &markers_14 },
    .{ .rel = "zigux/tests/phase3_export_shim_build.zig", .markers = &markers_15 },
    .{ .rel = "zigux/tests/phase3_export_uapi_layout.zig", .markers = &markers_16 },
    .{ .rel = "zigux/tests/phase3_export_uapi_layout_build.zig", .markers = &markers_17 },
    .{ .rel = "zigux/tests/phase3_export_uapi_c_header_smoke.c", .markers = &markers_18 },
    .{ .rel = "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig", .markers = &markers_19 },
    .{ .rel = "scripts/zigux/check_phase3_dev_t_starter_packet.zig", .markers = &markers_20 },
    .{ .rel = "scripts/zigux/check_phase3_catalog_selftest.zig", .markers = &markers_21 },
    .{ .rel = "scripts/zigux/validate_phase3_selftest.zig", .markers = &markers_22 },
    .{ .rel = "scripts/zigux/run_phase3_checks.zig", .markers = &markers_23 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
