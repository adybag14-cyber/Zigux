const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_DEV_T_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_DEV_T_STARTER_PACKET=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "zigux/bindings/abi.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
};

const markers_1 = [_][]const u8{
    "zigux/bindings/abi.zig",
    "zigux/bindings/version.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "the broader export/UAPI survey, catalog, or shared Phase 3 replay packet",
};

const markers_2 = [_][]const u8{
    "#define ZIGUX_UAPI_ABI_MAJOR 0u",
    "#define ZIGUX_UAPI_ABI_MINOR 1u",
    "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
    "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
    "struct zigux_uapi_version {",
    "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
};

const markers_3 = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
    "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
    "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u",
    "#define ZIGUX_DEV_T_MINOR_OFFSET 4u",
    "struct zigux_dev_t_fields {",
    "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
};

const markers_4 = [_][]const u8{
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

const markers_5 = [_][]const u8{
    "pub const abi_major: u32 = 0;",
    "pub const abi_minor: u32 = 1;",
    "pub const header_family_revision: u32 = 1;",
    "pub const Version = extern struct {",
    "pub fn current() Version {",
    "std.debug.assert(version_size == 12);",
    "std.debug.assert(version_align == 4);",
};

const markers_6 = [_][]const u8{
    "pub const ABI_VERSION: u16 = 1;",
    "pub const STATUS_FLAG_ERROR: u16 = 1;",
    "pub const BoundaryHeader = extern struct {",
    "pub const ExportStatus = extern struct {",
    "pub const Facility = enum(u16) {",
    "pub fn defaultHeader(flags: u16) BoundaryHeader {",
};

const markers_7 = [_][]const u8{
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

const markers_8 = [_][]const u8{
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

const markers_9 = [_][]const u8{
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

const markers_10 = [_][]const u8{
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

const markers_11 = [_][]const u8{
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

const markers_12 = [_][]const u8{
    "\"slug\": \"phase3-dev-t-starter-packet\"",
    "\"status\": \"starter_packet_present\"",
    "\"scope\": \"starter Linux-facing header family plus dev_t, version, and export shim replay\"",
    "\"Documentation/zigux/phase3-abi-slice.md\"",
    "\"Documentation/zigux/phase3-validator-support-surface.md\"",
    "\"zigux/bindings/abi.zig\"",
    "\"zigux/bindings/version.zig\"",
    "\"zigux/kernel/export_shim.zig\"",
    "\"zigux/tests/phase3_dev_t_starter_packet_manifest.json\"",
    "\"next_safe_step\": \"keep the live starter packet honest with bounded manifest-backed checker and compile replay work before widening the broader Phase 3 ABI substrate\"",
};

const markers_13 = [_][]const u8{
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-abi-slice.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase3-validator-support-surface.md", .markers = &markers_1 },
    .{ .rel = "include/linux/zigux.h", .markers = &markers_2 },
    .{ .rel = "include/zigux/dev_t.h", .markers = &markers_3 },
    .{ .rel = "zigux/uapi/dev_t.zig", .markers = &markers_4 },
    .{ .rel = "zigux/uapi/version.zig", .markers = &markers_5 },
    .{ .rel = "zigux/bindings/abi.zig", .markers = &markers_6 },
    .{ .rel = "zigux/bindings/dev_t.zig", .markers = &markers_7 },
    .{ .rel = "zigux/bindings/version.zig", .markers = &markers_8 },
    .{ .rel = "zigux/kernel/export_shim.zig", .markers = &markers_9 },
    .{ .rel = "zigux/tests/phase3_dev_t_starter_packet.zig", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase3_dev_t_starter_packet_build.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase3_dev_t_starter_packet_manifest.json", .markers = &markers_12 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_13 },
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
