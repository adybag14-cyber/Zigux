const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_DEV_T_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass";

const COMPILE_ROUTE = [_][]const u8{
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-abi-slice_md = [_][]const u8{
    "zigux/bindings/abi.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "zigux/bindings/abi.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "the broader export/UAPI survey, catalog, or shared Phase 3 replay packet",
};

const REQUIRED_MARKERS__include_linux_zigux_h = [_][]const u8{
    "#define ZIGUX_UAPI_ABI_MAJOR 0u",
    "#define ZIGUX_UAPI_ABI_MINOR 1u",
    "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
    "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
    "struct zigux_uapi_version {",
    "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
};

const REQUIRED_MARKERS__include_zigux_dev_t_h = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
    "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
    "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u",
    "#define ZIGUX_DEV_T_MINOR_OFFSET 4u",
    "struct zigux_dev_t_fields {",
    "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
};

const REQUIRED_MARKERS__zigux_uapi_dev_t_zig = [_][]const u8{
    "pub const abi_version: u32 = 1;",
    "pub const Fields = extern struct {",
    "pub const fields_size: usize = @sizeOf(Fields);",
    "pub const fields_align: usize = @alignOf(Fields);",
    "pub const major_offset: usize = @offsetOf(Fields, \"major\");",
    "pub const minor_offset: usize = @offsetOf(Fields, \"minor\");",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
    "std.debug.assert(fields_size == 8);",
    "std.debug.assert(fields_align == 4);",
    "std.debug.assert(major_offset == 0);",
    "std.debug.assert(minor_offset == 4);",
    "std.debug.assert(major_bits + minor_bits == 32);",
};

const REQUIRED_MARKERS__zigux_uapi_version_zig = [_][]const u8{
    "pub const abi_major: u32 = 0;",
    "pub const abi_minor: u32 = 1;",
    "pub const header_family_revision: u32 = 1;",
    "pub const Version = extern struct {",
    "pub fn current() Version {",
    "std.debug.assert(version_size == 12);",
    "std.debug.assert(version_align == 4);",
};

const REQUIRED_MARKERS__zigux_bindings_abi_zig = [_][]const u8{
    "pub const ABI_VERSION: u16 = 1;",
    "pub const STATUS_FLAG_ERROR: u16 = 1;",
    "pub const BoundaryHeader = extern struct {",
    "pub const ExportStatus = extern struct {",
    "pub const Facility = enum(u16) {",
    "pub fn defaultHeader(flags: u16) BoundaryHeader {",
};

const REQUIRED_MARKERS__zigux_bindings_dev_t_zig = [_][]const u8{
    "pub const abi_version = uapi.abi_version;",
    "pub const fields_size = uapi.fields_size;",
    "pub const fields_align = uapi.fields_align;",
    "pub const major_offset = uapi.major_offset;",
    "pub const minor_offset = uapi.minor_offset;",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn eql(left: Fields, right: Fields) bool {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
    "std.debug.assert(major_offset == 0);",
    "std.debug.assert(minor_offset == 4);",
};

const REQUIRED_MARKERS__zigux_bindings_version_zig = [_][]const u8{
    "pub const abi_major = uapi.abi_major;",
    "pub const abi_minor = uapi.abi_minor;",
    "pub const header_family_revision = uapi.header_family_revision;",
    "pub const version_size: usize = uapi.version_size;",
    "pub const version_align: usize = uapi.version_align;",
    "pub const abi_major_offset: usize = uapi.abi_major_offset;",
    "pub const abi_minor_offset: usize = uapi.abi_minor_offset;",
    "pub const header_family_revision_offset: usize = uapi.header_family_revision_offset;",
    "pub fn current() Version {",
    "pub fn eql(left: Version, right: Version) bool {",
    "std.debug.assert(header_family_revision_offset == 8);",
};

const REQUIRED_MARKERS__zigux_kernel_export_shim_zig = [_][]const u8{
    "const abi = @import(\"abi_bindings\");",
    "const dev_t = @import(\"dev_t_binding\");",
    "const version = @import(\"version_binding\");",
    "pub const BoundaryHeader = abi.BoundaryHeader;",
    "pub const ExportStatus = abi.ExportStatus;",
    "pub const Facility = abi.Facility;",
    "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
    "pub fn currentVersion() Version {",
    "pub fn makeDevTFields(major: u32, minor: u32) DevTFields {",
    "pub fn okStatus(facility: Facility) ExportStatus {",
    "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
    "pub fn validateDeviceFields(fields: DevTFields) ExportStatus {",
    "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_zig = [_][]const u8{
    "const uapi_dev_t = @import(\"uapi_dev_t\");",
    "const export_shim = @import(\"export_shim\");",
    "test \"dev_t starter binding preserves the current ABI layout\" {",
    "test \"dev_t starter binding stays aligned with the UAPI field offsets\" {",
    "test \"starter packet version binding preserves the Linux-facing header family layout\" {",
    "test \"dev_t binding equality stays field based\" {",
    "test \"starter dev_t validation keeps the boundary range explicit\" {",
    "test \"version binding equality stays field based\" {",
    "test \"starter export shim reuses the canonical boundary header and version snapshot\" {",
    "test \"starter export shim keeps facility-tagged status helpers explicit\" {",
    "test \"starter export shim forwards dev_t fields without changing starter layout semantics\" {",
    "test \"starter export shim relays dev_t validation status\" {",
    "try testing.expectEqual(@as(u32, 1), dev_t.abi_version);",
    "try testing.expectEqual(uapi_dev_t.major_offset, dev_t.major_offset);",
    "try testing.expect(dev_t.eql(left, same));",
    "try testing.expect(dev_t.validate(valid));",
    "try testing.expect(version.eql(current, same));",
    "const header = export_shim.canonicalHeader(0x41);",
    "const ok = export_shim.okStatus(.helpers);",
    "const fields = export_shim.makeDevTFields(11, 29);",
    "const valid = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../bindings/dev_t.zig\"),",
    ".root_source_file = b.path(\"../bindings/version.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    ".root_source_file = b.path(\"phase3_dev_t_starter_packet.zig\"),",
    "dev_t_binding.addImport(\"uapi_dev_t\", uapi_dev_t);",
    "version_binding.addImport(\"uapi_version\", uapi_version);",
    "export_shim.addImport(\"abi_bindings\", abi_bindings);",
    "export_shim.addImport(\"dev_t_binding\", dev_t_binding);",
    "export_shim.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"uapi_dev_t\", uapi_dev_t);",
    "root_module.addImport(\"dev_t_binding\", dev_t_binding);",
    "root_module.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"export_shim\", export_shim);",
    "\"phase3-dev-t-starter-packet-test\"",
    "\"Run the Phase 3 dev_t starter-packet ABI self-check\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-dev-t-starter-packet\"",
    "\"status\": \"starter_packet_present\"",
    "\"scope\": \"starter Linux-facing header family plus dev_t, version, and export shim replay\"",
    "\"Documentation/zigux/phase3-abi-slice.md\"",
    "\"Documentation/zigux/phase3-validator-support-surface.md\"",
    "\"zigux/bindings/abi.zig\"",
    "\"zigux/bindings/version.zig\"",
    "\"zigux/kernel/export_shim.zig\"",
    "\"zigux/tests/phase3_dev_t_starter_packet_manifest.json\"",
    "\"zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig\"",
    "\"next_safe_step\": \"keep the live starter packet honest with bounded manifest-backed checker and compile replay work before widening the broader Phase 3 ABI substrate\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "zigux/kernel/export_shim.zig",
    "zigux/kernel/export_shim.zig",
    "pub const major_offset: usize = @offsetOf(Fields, \"major\");",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
    "pub const header_family_revision: u32 = 1;",
    "pub fn defaultHeader(flags: u16) BoundaryHeader {",
    "pub const major_offset = uapi.major_offset;",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
    "pub const version_size: usize = uapi.version_size;",
    "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
    "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
    "test \"starter export shim reuses the canonical boundary header and version snapshot\" {",
    "const valid = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);",
    "root_module.addImport(\"export_shim\", export_shim);",
    "\"zigux/kernel/export_shim.zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_compile_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_compile_route_path);
    const text_compile_route = try guard.readUtf8File(io, allocator, text_compile_route_path);
    defer allocator.free(text_compile_route);
    for (COMPILE_ROUTE) |marker| try guard.requireMarker(text_compile_route, marker);
    const text_required_markers__documentation_zigux_phase3-abi-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-abi-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-abi-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-abi-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-abi-slice_md, marker);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-validator-support-surface/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-validator-support-surface_md, marker);
    const text_required_markers__include_linux_zigux_h_path = try guard.joinPath(allocator, root, "include/linux/zigux/h");
    defer allocator.free(text_required_markers__include_linux_zigux_h_path);
    const text_required_markers__include_linux_zigux_h = try guard.readUtf8File(io, allocator, text_required_markers__include_linux_zigux_h_path);
    defer allocator.free(text_required_markers__include_linux_zigux_h);
    for (REQUIRED_MARKERS__include_linux_zigux_h) |marker| try guard.requireMarker(text_required_markers__include_linux_zigux_h, marker);
    const text_required_markers__include_zigux_dev_t_h_path = try guard.joinPath(allocator, root, "include/zigux/dev/t/h");
    defer allocator.free(text_required_markers__include_zigux_dev_t_h_path);
    const text_required_markers__include_zigux_dev_t_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_dev_t_h_path);
    defer allocator.free(text_required_markers__include_zigux_dev_t_h);
    for (REQUIRED_MARKERS__include_zigux_dev_t_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_dev_t_h, marker);
    const text_required_markers__zigux_uapi_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig_path);
    const text_required_markers__zigux_uapi_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_uapi_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_dev_t_zig, marker);
    const text_required_markers__zigux_uapi_version_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/version/zig");
    defer allocator.free(text_required_markers__zigux_uapi_version_zig_path);
    const text_required_markers__zigux_uapi_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_version_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_version_zig);
    for (REQUIRED_MARKERS__zigux_uapi_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_version_zig, marker);
    const text_required_markers__zigux_bindings_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig_path);
    const text_required_markers__zigux_bindings_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_abi_zig, marker);
    const text_required_markers__zigux_bindings_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig_path);
    const text_required_markers__zigux_bindings_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_bindings_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_dev_t_zig, marker);
    const text_required_markers__zigux_bindings_version_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/version/zig");
    defer allocator.free(text_required_markers__zigux_bindings_version_zig_path);
    const text_required_markers__zigux_bindings_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_version_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_version_zig);
    for (REQUIRED_MARKERS__zigux_bindings_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_version_zig, marker);
    const text_required_markers__zigux_kernel_export_shim_zig_path = try guard.joinPath(allocator, root, "zigux/kernel/export/shim/zig");
    defer allocator.free(text_required_markers__zigux_kernel_export_shim_zig_path);
    const text_required_markers__zigux_kernel_export_shim_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_kernel_export_shim_zig_path);
    defer allocator.free(text_required_markers__zigux_kernel_export_shim_zig);
    for (REQUIRED_MARKERS__zigux_kernel_export_shim_zig) |marker| try guard.requireMarker(text_required_markers__zigux_kernel_export_shim_zig, marker);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/dev/t/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/dev/t/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/dev/t/starter/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_dev_t_starter_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_dev_t_starter_packet_manifest_json, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
