const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_DEV_T_LAYOUT=pass";
pub const self_test_pass_marker = "PHASE3_DEV_T_LAYOUT_SELF_TEST=pass";

const REQUIRED_HEADER_MARKERS = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
    "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
    "struct zigux_dev_t_fields {",
    "uint32_t major;",
    "uint32_t minor;",
};

const REQUIRED_UAPI_MARKERS = [_][]const u8{
    "pub const abi_version: u32 = 1;",
    "pub const Fields = extern struct {",
    "major: u32,",
    "minor: u32,",
};

const REQUIRED_BINDING_MARKERS = [_][]const u8{
    "pub const fields_size: usize = @sizeOf(uapi.Fields);",
    "pub const fields_align: usize = @alignOf(uapi.Fields);",
    "pub const major_offset: usize = @offsetOf(uapi.Fields, \"major\");",
    "pub const minor_offset: usize = @offsetOf(uapi.Fields, \"minor\");",
    "std.debug.assert(fields_size == 8);",
    "std.debug.assert(fields_align == 4);",
    "std.debug.assert(major_offset == 0);",
    "std.debug.assert(minor_offset == 4);",
};

const REQUIRED_TEST_MARKERS = [_][]const u8{
    "test \"dev_t starter binding preserves the current ABI layout\" {",
    "test \"starter packet version stays aligned with the Linux-facing header family\" {",
    "test \"dev_t binding equality stays field based\" {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_header_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_dev_t/expected.json");
    defer allocator.free(text_required_header_markers_path);
    const text_required_header_markers = try guard.readUtf8File(io, allocator, text_required_header_markers_path);
    defer allocator.free(text_required_header_markers);
    for (REQUIRED_HEADER_MARKERS) |marker| try guard.requireMarker(text_required_header_markers, marker);
    const text_required_uapi_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_dev_t/expected.json");
    defer allocator.free(text_required_uapi_markers_path);
    const text_required_uapi_markers = try guard.readUtf8File(io, allocator, text_required_uapi_markers_path);
    defer allocator.free(text_required_uapi_markers);
    for (REQUIRED_UAPI_MARKERS) |marker| try guard.requireMarker(text_required_uapi_markers, marker);
    const text_required_binding_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_dev_t/expected.json");
    defer allocator.free(text_required_binding_markers_path);
    const text_required_binding_markers = try guard.readUtf8File(io, allocator, text_required_binding_markers_path);
    defer allocator.free(text_required_binding_markers);
    for (REQUIRED_BINDING_MARKERS) |marker| try guard.requireMarker(text_required_binding_markers, marker);
    const text_required_test_markers_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_dev_t/expected.json");
    defer allocator.free(text_required_test_markers_path);
    const text_required_test_markers = try guard.readUtf8File(io, allocator, text_required_test_markers_path);
    defer allocator.free(text_required_test_markers);
    for (REQUIRED_TEST_MARKERS) |marker| try guard.requireMarker(text_required_test_markers, marker);
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
