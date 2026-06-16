const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE=pass";
pub const self_test_pass_marker = "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass";

const ROLE_MARKER = [_][]const u8{
    "PHASE3_ZIGUX_H_ROLE=linux-facing relay and aggregation header for already-landed ABI, boundary-header compatibility, starter dev_t review surfaces, and starter interop-policy and rbtree predicate relays only",
};

const HEADER_FAMILY_MACRO_MARKER = [_][]const u8{
    "PHASE3_ZIGUX_H_HEADER_FAMILY_MACROS=ZIGUX_UAPI_ABI_MAJOR, ZIGUX_UAPI_ABI_MINOR, ZIGUX_UAPI_HEADER_FAMILY_REVISION, ZIGUX_UAPI_DEV_T_PACKET_PRESENT, and ZIGUX_UAPI_INVALID_ARGUMENT stay starter relay markers in include/linux/zigux.h rather than becoming new canonical owner definitions",
};

const HEADER_INCLUDE_MARKERS = [_][]const u8{
    "#include <zigux/abi.h>",
    "#include <zigux/dev_t.h>",
};

const HEADER_DEFINE_MARKERS = [_][]const u8{
    "#define ZIGUX_UAPI_ABI_MAJOR 0u",
    "#define ZIGUX_UAPI_ABI_MINOR 1u",
    "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
    "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
    "#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)",
};

const HEADER_HELPERS = [_][]const u8{
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

const NOTE_HELPERS = [_][]const u8{
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

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_role_marker_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_role_marker_path);
    const text_role_marker = try guard.readUtf8File(io, allocator, text_role_marker_path);
    defer allocator.free(text_role_marker);
    for (ROLE_MARKER) |marker| try guard.requireMarker(text_role_marker, marker);
    const text_header_family_macro_marker_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_header_family_macro_marker_path);
    const text_header_family_macro_marker = try guard.readUtf8File(io, allocator, text_header_family_macro_marker_path);
    defer allocator.free(text_header_family_macro_marker);
    for (HEADER_FAMILY_MACRO_MARKER) |marker| try guard.requireMarker(text_header_family_macro_marker, marker);
    const text_header_include_markers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_header_include_markers_path);
    const text_header_include_markers = try guard.readUtf8File(io, allocator, text_header_include_markers_path);
    defer allocator.free(text_header_include_markers);
    for (HEADER_INCLUDE_MARKERS) |marker| try guard.requireMarker(text_header_include_markers, marker);
    const text_header_define_markers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_header_define_markers_path);
    const text_header_define_markers = try guard.readUtf8File(io, allocator, text_header_define_markers_path);
    defer allocator.free(text_header_define_markers);
    for (HEADER_DEFINE_MARKERS) |marker| try guard.requireMarker(text_header_define_markers, marker);
    const text_header_helpers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_header_helpers_path);
    const text_header_helpers = try guard.readUtf8File(io, allocator, text_header_helpers_path);
    defer allocator.free(text_header_helpers);
    for (HEADER_HELPERS) |marker| try guard.requireMarker(text_header_helpers, marker);
    const text_note_helpers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_note_helpers_path);
    const text_note_helpers = try guard.readUtf8File(io, allocator, text_note_helpers_path);
    defer allocator.free(text_note_helpers);
    for (NOTE_HELPERS) |marker| try guard.requireMarker(text_note_helpers, marker);
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
