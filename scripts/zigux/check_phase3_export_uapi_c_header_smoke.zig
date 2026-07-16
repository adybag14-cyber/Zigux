const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass";
pub const self_test_pass_marker = "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass",
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "#include <linux/zigux.h>",
    "static int check_version_relays(void)",
    "zigux_uapi_version_current()",
    "zigux_uapi_version_has_current_abi_major(",
    "zigux_uapi_version_has_current_abi_minor(",
    "zigux_uapi_version_has_current_header_family_revision(",
    "zigux_uapi_version_matches_current(",
    "zigux_uapi_validate_version(",
    "if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "static int check_boundary_header_relays(void)",
    "zigux_boundary_header_make(",
    "zigux_boundary_header_make_compatible(",
    "zigux_validate_boundary_header(",
    "zigux_boundary_header_is_current_abi_version(",
    "zigux_boundary_header_is_compatible_size(",
    "zigux_boundary_header_is_canonical_size(",
    "if (!zigux_boundary_header_is_compatible(canonical))",
    "zigux_boundary_header_is_canonical(",
    "zigux_boundary_header_extends_boundary(",
    "zigux_boundary_header_requested_extra_bytes(",
    "if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)",
    "zigux_boundary_header_canonicalize(",
    "struct zigux_export_status stale_status =",
    "struct zigux_export_status uapi_undersized_status =",
    "struct zigux_export_status uapi_stale_status =",
    "if (stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "if (uapi_undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)",
    "static int check_dev_t_relays(void)",
    "struct zigux_dev_t_fields invalid_major =",
    "struct zigux_dev_t_fields invalid_minor =",
    "zigux_uapi_validate_dev_t_fields(",
    "zigux_uapi_validate_dev_t_components(",
    "zigux_uapi_validate_dev_t_range(",
    "zigux_uapi_dev_t_fields_range_is_valid(",
    "struct zigux_export_status invalid_field_status =",
    "struct zigux_export_status invalid_minor_status =",
    "if (invalid_field_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    "int main(void)",
};

const markers_1 = [_][]const u8{
    "zigux_uapi_version_current(",
    "zigux_uapi_version_has_current_abi_major(",
    "zigux_uapi_version_has_current_abi_minor(",
    "zigux_uapi_version_has_current_header_family_revision(",
    "zigux_uapi_version_matches_current(",
    "zigux_uapi_validate_version(",
    "zigux_uapi_boundary_header_current(",
    "zigux_uapi_boundary_header_compatible(",
    "zigux_uapi_validate_boundary_header(",
    "zigux_uapi_boundary_header_has_current_abi_version(",
    "static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)",
    "static inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)",
    "zigux_uapi_boundary_header_is_canonical(",
    "zigux_uapi_boundary_header_is_compatible(",
    "zigux_uapi_boundary_header_extends_boundary(",
    "zigux_uapi_boundary_header_requested_extra_bytes(",
    "zigux_uapi_boundary_header_canonicalize(",
    "zigux_validate_boundary_header(",
    "zigux_boundary_header_make(",
    "zigux_boundary_header_make_compatible(",
    "zigux_boundary_header_is_current_abi_version(",
    "zigux_boundary_header_is_compatible_size(",
    "zigux_boundary_header_is_canonical_size(",
    "zigux_boundary_header_is_compatible(",
    "zigux_boundary_header_is_canonical(",
    "zigux_boundary_header_extends_boundary(",
    "zigux_boundary_header_requested_extra_bytes(",
    "zigux_boundary_header_canonicalize(",
    "zigux_uapi_validate_dev_t_fields(",
    "zigux_uapi_validate_dev_t_components(",
    "zigux_uapi_validate_dev_t_range(",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/phase3_export_uapi_c_header_smoke.c", .markers = &markers_0 },
    .{ .rel = "include/linux/zigux.h", .markers = &markers_1 },
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
