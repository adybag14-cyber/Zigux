const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "validated Documentation/zigux/phase3-linux-zigux-header-governance.md";
pub const self_test_pass_marker = "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",
};

const live_output_markers = [_][]const u8{
    "validated Documentation/zigux/phase3-linux-zigux-header-governance.md",
};

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed ABI, boundary-header compatibility, starter dev_t review surfaces, and starter interop-policy and rbtree predicate relays only",
    "PHASE3_ZIGUX_H_HEADER_FAMILY_MACROS=ZIGUX_UAPI_ABI_MAJOR, ZIGUX_UAPI_ABI_MINOR, ZIGUX_UAPI_HEADER_FAMILY_REVISION, ZIGUX_UAPI_DEV_T_PACKET_PRESENT, and ZIGUX_UAPI_INVALID_ARGUMENT stay starter relay markers in include/linux/zigux.h rather than becoming new canonical owner definitions",
    "`zigux_uapi_version_current()`",
    "`zigux_uapi_version_has_current_*()`",
    "`zigux_uapi_version_matches_current()`",
    "`zigux_uapi_validate_version()`",
    "`zigux_uapi_boundary_header_current()`",
    "`zigux_uapi_boundary_header_compatible()`",
    "`zigux_uapi_boundary_header_has_current_abi_version()`",
    "`zigux_uapi_boundary_header_is_canonical()`",
    "`zigux_uapi_boundary_header_is_compatible()`",
    "`zigux_uapi_boundary_header_extends_boundary()`",
    "`zigux_uapi_boundary_header_requested_extra_bytes()`",
    "`zigux_uapi_boundary_header_canonicalize()`",
    "`zigux_uapi_validate_boundary_header()`",
    "`zigux_boundary_header_make()`",
    "`zigux_boundary_header_make_compatible()`",
    "`zigux_boundary_header_is_current_abi_version()`",
    "`zigux_boundary_header_is_compatible_size()`",
    "`zigux_boundary_header_is_canonical_size()`",
    "`zigux_boundary_header_is_compatible()`",
    "`zigux_boundary_header_is_canonical()`",
    "`zigux_boundary_header_extends_boundary()`",
    "`zigux_boundary_header_requested_extra_bytes()`",
    "`zigux_boundary_header_canonicalize()`",
    "`zigux_validate_boundary_header()`",
    "`zigux_uapi_dev_t_fields_is_valid()`",
    "`zigux_uapi_validate_dev_t_fields()`",
    "`zigux_uapi_validate_dev_t_components()`",
    "`zigux_uapi_dev_t_fields_range_is_valid()`",
    "`zigux_uapi_validate_dev_t_range()`",
};

const markers_1 = [_][]const u8{
    "#include <zigux/abi.h>",
    "#include <zigux/dev_t.h>",
    "#define ZIGUX_UAPI_ABI_MAJOR 0u",
    "#define ZIGUX_UAPI_ABI_MINOR 1u",
    "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
    "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
    "#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)",
    "zigux_uapi_version_current",
    "zigux_uapi_version_has_current_abi_major",
    "zigux_uapi_version_has_current_abi_minor",
    "zigux_uapi_version_has_current_header_family_revision",
    "zigux_uapi_version_matches_current",
    "zigux_uapi_validate_version",
    "zigux_uapi_boundary_header_current",
    "zigux_uapi_boundary_header_compatible",
    "zigux_uapi_boundary_header_has_current_abi_version",
    "zigux_uapi_boundary_header_is_canonical",
    "zigux_uapi_boundary_header_is_compatible",
    "zigux_uapi_boundary_header_extends_boundary",
    "zigux_uapi_boundary_header_requested_extra_bytes",
    "zigux_uapi_boundary_header_canonicalize",
    "zigux_uapi_validate_boundary_header",
    "zigux_boundary_header_make",
    "zigux_boundary_header_make_compatible",
    "zigux_boundary_header_is_current_abi_version",
    "zigux_boundary_header_is_compatible_size",
    "zigux_boundary_header_is_canonical_size",
    "zigux_boundary_header_is_compatible",
    "zigux_boundary_header_is_canonical",
    "zigux_boundary_header_extends_boundary",
    "zigux_boundary_header_requested_extra_bytes",
    "zigux_boundary_header_canonicalize",
    "zigux_validate_boundary_header",
    "zigux_uapi_dev_t_fields_is_valid",
    "zigux_uapi_validate_dev_t_fields",
    "zigux_uapi_validate_dev_t_components",
    "zigux_uapi_dev_t_fields_range_is_valid",
    "zigux_uapi_validate_dev_t_range",
};

const markers_2 = [_][]const u8{
    "\"phase\": \"Phase 3\"",
    "\"replay_routes\"",
    "zig run scripts/zigux/validate_phase3_linux_zigux_header_governance.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_linux_zigux_header_governance.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-linux-zigux-header-governance.md", .markers = &markers_0 },
    .{ .rel = "include/linux/zigux.h", .markers = &markers_1 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_2 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "="))
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len })
        else
            try guard.printLine(io, "{s}", .{marker});
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
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
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
