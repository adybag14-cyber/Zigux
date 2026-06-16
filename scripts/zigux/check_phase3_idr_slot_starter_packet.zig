const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDR_SLOT_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_xa_value_zig = [_][]const u8{
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "pub fn makeValue(value: usize) MakeValueError!usize {",
};

const REQUIRED_MARKERS__zigux_helpers_xarray_slot_view_zig = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromErrorCode(code: isize) SlotView {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_idr_slot_view_zig = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromInternalValue(value: usize) xa_value.MakeValueError!SlotView {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
    "test \"empty slots stay distinct from pointer and internal lanes\" {",
    "test \"xa_value-tagged entries stay internal instead of looking like mapped pointers\" {",
    "test \"err_ptr encodings stay separated from pointer-backed idr entries\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_idr_slot_starter_packet_zig = [_][]const u8{
    "test \"idr slot view keeps empty slots explicit\" {",
    "test \"idr slot view keeps pointer lanes publishable without tagging drift\" {",
    "test \"idr slot view keeps xa_value entries in the internal lane\" {",
    "test \"idr slot view preserves err_ptr encodings as tagged error entries\" {",
    "test \"top err_ptr encoding never falls back into the pointer lane\" {",
    "try testing.expect(idr_slot_view.isTaggedInternalEntry(raw));",
};

const REQUIRED_MARKERS__zigux_tests_phase3_idr_slot_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/idr_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_idr_slot_starter_packet.zig\"),",
    "idr_slot_view.addImport(\"xarray_slot_view\", xarray_slot_view);",
    "idr_slot_view.addImport(\"xa_value\", xa_value);",
    "\"phase3-idr-slot-starter-packet-test\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "pub const SlotKind = enum {",
    "test \"idr slot view keeps empty slots explicit\" {",
    "\"phase3-idr-slot-starter-packet-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_helpers_xa_value_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/xa/value/zig");
    defer allocator.free(text_required_markers__zigux_helpers_xa_value_zig_path);
    const text_required_markers__zigux_helpers_xa_value_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_xa_value_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_xa_value_zig);
    for (REQUIRED_MARKERS__zigux_helpers_xa_value_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_xa_value_zig, marker);
    const text_required_markers__zigux_helpers_xarray_slot_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/xarray/slot/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_xarray_slot_view_zig_path);
    const text_required_markers__zigux_helpers_xarray_slot_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_xarray_slot_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_xarray_slot_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_xarray_slot_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_xarray_slot_view_zig, marker);
    const text_required_markers__zigux_helpers_idr_slot_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/idr/slot/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_idr_slot_view_zig_path);
    const text_required_markers__zigux_helpers_idr_slot_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_idr_slot_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_idr_slot_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_idr_slot_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_idr_slot_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/idr/slot/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_idr_slot_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/idr/slot/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_idr_slot_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_idr_slot_starter_packet_build_zig, marker);
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
