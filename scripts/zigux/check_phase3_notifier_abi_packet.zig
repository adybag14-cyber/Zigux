const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_NOTIFIER_ABI_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_NOTIFIER_ABI_PACKET_SELF_TEST=pass";

const COMPILE_ROUTE = [_][]const u8{
    "zig build phase3-notifier-abi-packet-test --build-file zigux/tests/phase3_notifier_abi_packet_build.zig",
};

const REQUIRED_MARKERS__include_zigux_abi_h = [_][]const u8{
    "#define ZIGUX_NOTIFIER_DONE 0U",
    "#define ZIGUX_NOTIFIER_OK 1U",
    "#define ZIGUX_NOTIFIER_STOP 2U",
    "struct zigux_notifier_block {",
    "uintptr_t notifier_call;",
    "uintptr_t next;",
    "int32_t priority;",
    "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
};

const REQUIRED_MARKERS__zigux_bindings_abi_zig = [_][]const u8{
    "const notifier_abi = @import(\"notifier_abi.zig\");",
    "pub const NOTIFIER_DONE: u32 = 0;",
    "pub const NOTIFIER_OK: u32 = 1;",
    "pub const NOTIFIER_STOP: u32 = 2;",
    "pub const NotifierResult = notifier_abi.NotifierResult;",
    "pub const NotifierBlock = notifier_abi.NotifierBlock;",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
};

const REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig = [_][]const u8{
    "pub const NotifierResult = enum(u32) {",
    "done = 0,",
    "ok = 1,",
    "stop = 2,",
    "pub const NotifierBlock = extern struct {",
    "notifier_call: usize,",
    "next: usize,",
    "priority: i32,",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_layout_assert_zig = [_][]const u8{
    "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
    "pub fn expectFieldLayout(",
};

const REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_zig = [_][]const u8{
    "const abi = @import(\"abi_bindings\");",
    "const layout_assert = @import(\"layout_assert\");",
    "test \"notifier binding keeps shared result values aligned\" {",
    "test \"notifier binding keeps published layout explicit\" {",
    "test \"notifier binding chain helper stays aligned with shared abi helper\" {",
    "test \"notifier binding preserves pointer-width links\" {",
    "std.mem.alignForward(usize, raw_size, @alignOf(usize));",
    "layout_assert.expectFieldLayout(abi.NotifierBlock, \"priority\", @sizeOf(usize) * 2);",
    "abi.chainHasNonincreasingPriority(&head)",
    "const middle_ptr: *const abi.NotifierBlock = @ptrFromInt(head.next);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"phase3_notifier_abi_packet.zig\"),",
    "root_module.addImport(\"abi_bindings\", abi_bindings);",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "\"phase3-notifier-abi-packet-test\"",
    "\"Run the Phase 3 notifier ABI packet self-check\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-notifier-abi-packet\"",
    "\"status\": \"shared_notifier_binding_present\"",
    "\"zigux/bindings/notifier_abi.zig\"",
    "\"zigux/helpers/layout_assert.zig\"",
    "\"scripts\\zigux/check_phase3_notifier_abi_packet.zig\"",
    "\"zig run scripts\\zigux/check_phase3_notifier_abi_packet.zig -- --self-test\"",
    "\"scripts\\zigux/check_phase3_abi.zig\"",
    "\"scripts\\zigux/validate_phase3.zig\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "pub const NotifierBlock = notifier_abi.NotifierBlock;",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    "pub fn expectFieldLayout(",
    "test \"notifier binding preserves pointer-width links\" {",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "\"scripts\\zigux/validate_phase3.zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_compile_route_path = try guard.joinPath(allocator, root, "include/zigux/abi.h");
    defer allocator.free(text_compile_route_path);
    const text_compile_route = try guard.readUtf8File(io, allocator, text_compile_route_path);
    defer allocator.free(text_compile_route);
    for (COMPILE_ROUTE) |marker| try guard.requireMarker(text_compile_route, marker);
    const text_required_markers__include_zigux_abi_h_path = try guard.joinPath(allocator, root, "include/zigux/abi/h");
    defer allocator.free(text_required_markers__include_zigux_abi_h_path);
    const text_required_markers__include_zigux_abi_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_abi_h_path);
    defer allocator.free(text_required_markers__include_zigux_abi_h);
    for (REQUIRED_MARKERS__include_zigux_abi_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_abi_h, marker);
    const text_required_markers__zigux_bindings_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig_path);
    const text_required_markers__zigux_bindings_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_abi_zig, marker);
    const text_required_markers__zigux_bindings_notifier_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/notifier/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig_path);
    const text_required_markers__zigux_bindings_notifier_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_notifier_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_notifier_abi_zig, marker);
    const text_required_markers__zigux_helpers_layout_assert_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/layout/assert/zig");
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig_path);
    const text_required_markers__zigux_helpers_layout_assert_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_layout_assert_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig);
    for (REQUIRED_MARKERS__zigux_helpers_layout_assert_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_layout_assert_zig, marker);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/notifier/abi/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_notifier_abi_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/notifier/abi/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_notifier_abi_packet_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/notifier/abi/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_notifier_abi_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_notifier_abi_packet_manifest_json, marker);
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
