const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDA_SLOT=pass";
pub const self_test_pass_marker = "PHASE3_IDA_SLOT_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_helpers_ida_slot_view_zig = [_][]const u8{
    "pub const inline_bit_capacity: usize = @bitSizeOf(usize) - 1;",
    "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {",
    "pub fn fromUnexpectedError(code: isize) SlotView {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_dump_zig = [_][]const u8{
    "const ida_slot_view = @import(\"ida_slot_view\");",
    ".unexpected_err => \"unexpected_err\",",
    "try writeCase(writer, \"unexpected_err\", ida_slot_view.fromUnexpectedError(-22).rawValue(), false);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_slot_view.zig\"),",
    "\"phase3-ida-slot-dump\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c = [_][]const u8{
    "#define INLINE_BIT_CAPACITY ((unsigned)(sizeof(uintptr_t) * 8U - 1U))",
    "return \"unexpected_err\";",
    "write_case(\"unexpected_err\", (uintptr_t)(intptr_t)-22, false);",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_expected_json = [_][]const u8{
    "\"inline_bit_capacity\": 63",
    "\"name\": \"inline_top\"",
    "\"unexpected_error\": -22",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-ida-slot\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zig run scripts\\zigux/check_phase3_ida_slot.zig -- --repo-root . --zig zig --cc gcc\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_helpers_ida_slot_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/ida/slot/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_ida_slot_view_zig_path);
    const text_required_markers__zigux_helpers_ida_slot_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_ida_slot_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_ida_slot_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_ida_slot_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_ida_slot_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_slot_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/slot/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_slot_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_slot_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_slot_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/slot/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_slot_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_slot_dump_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/slot/phase3/ida/slot/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_phase3_ida_slot_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/slot/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/slot/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_slot_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_slot_manifest_json, marker);
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
