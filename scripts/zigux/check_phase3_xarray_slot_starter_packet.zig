const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_XARRAY_SLOT_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_err_ptr_zig = [_][]const u8{
    "pub const max_errno: usize = 4095;",
    "pub fn isErrValue(raw: usize) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_xa_value_zig = [_][]const u8{
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "pub fn makeValue(value: usize) MakeValueError!usize {",
};

const REQUIRED_MARKERS__zigux_helpers_xarray_slot_view_zig = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
    "test \"err floor stays in the err lane even with the xa_value low tag bit set\" {",
    "test \"gap below err floor stays pointer-like and leaves tagged decoders closed\" {",
    "test \"inline zero stays a tagged value and keeps other decoders closed\" {",
    "test \"top err_ptr encoding stays tagged and keeps value and pointer decoders closed\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_starter_packet_zig = [_][]const u8{
    "test \"xarray slot view keeps null slots explicit\" {",
    "test \"xarray slot view keeps xa_value entries out of the err_ptr band\" {",
    "test \"xarray slot view preserves err_ptr encodings as tagged error entries\" {",
    "test \"xarray slot view keeps ordinary pointer-like slots separate from tagged entries\" {",
    "test \"safe inline limit still lands in the tagged-value lane\" {",
    "test \"inline zero stays tagged without looking like a null slot\" {",
    "test \"top err_ptr encoding stays tagged and never falls back to pointer-like\" {",
    "try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));",
};

const REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_starter_packet.zig\"),",
    "xarray_slot_view.addImport(\"err_ptr\", err_ptr);",
    "xarray_slot_view.addImport(\"xa_value\", xa_value);",
    "\"phase3-xarray-slot-starter-packet-test\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "pub const SlotKind = enum {",
    "test \"xarray slot view keeps null slots explicit\" {",
    "\"phase3-xarray-slot-starter-packet-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_helpers_err_ptr_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/err/ptr/zig");
    defer allocator.free(text_required_markers__zigux_helpers_err_ptr_zig_path);
    const text_required_markers__zigux_helpers_err_ptr_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_err_ptr_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_err_ptr_zig);
    for (REQUIRED_MARKERS__zigux_helpers_err_ptr_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_err_ptr_zig, marker);
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
    const text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/xarray/slot/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/xarray/slot/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_xarray_slot_starter_packet_build_zig, marker);
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
