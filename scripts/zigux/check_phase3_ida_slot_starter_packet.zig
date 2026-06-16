const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDA_SLOT_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_IDA_SLOT_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_ida_slot_view_zig = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {",
    "pub fn fromBitmapPointer(pointer: usize) SlotView {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_starter_packet_zig = [_][]const u8{
    "test \"ida slot view keeps empty slots explicit\" {",
    "test \"ida slot view keeps inline mask lanes bounded to the helper-local packet\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_slot_view.zig\"),",
    "\"phase3-ida-slot-starter-packet-test\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-ida-slot\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_ida_slot_dump.zig\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {",
    "test \"ida slot view keeps inline mask lanes bounded to the helper-local packet\" {",
    "\"phase3-ida-slot-starter-packet-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_helpers_ida_slot_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/ida/slot/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_ida_slot_view_zig_path);
    const text_required_markers__zigux_helpers_ida_slot_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_ida_slot_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_ida_slot_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_ida_slot_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_ida_slot_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/slot/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/slot/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_slot_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/slot/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json, marker);
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
