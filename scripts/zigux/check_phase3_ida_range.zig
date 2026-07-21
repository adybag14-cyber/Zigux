const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDA_RANGE=pass";
pub const self_test_pass_marker = "PHASE3_IDA_RANGE_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-ida-range-slice_md = [_][]const u8{
    "# Phase 3 ida-range Slice",
    "`zigux/helpers/ida_range_view.zig`",
    "`zigux/tests/phase3_ida_range_dump.zig`",
    "`scripts\\zigux/check_phase3_ida_range.zig`",
    "`zig run scripts\\zigux/check_phase3_ida_range.zig -- --repo-root . --zig zig --cc gcc`",
    "helper-local ida range packet",
};

const REQUIRED_MARKERS__zigux_helpers_ida_range_view_zig = [_][]const u8{
    "pub const ClampedWindow = struct {",
    "pub const RangeSummary = struct {",
    "pub fn firstAllocatedInRange(self: RangeView, alloc_range: AllocationRange) ?Selection {",
    "pub fn summarize(self: RangeView, alloc_range: AllocationRange) ?RangeSummary {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_range_starter_packet_zig = [_][]const u8{
    "test \"ida range starter packet keeps partial allocation counting explicit\" {",
    "test \"ida range starter packet keeps ordered-range failure explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_range_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_range_view.zig\"),",
    "\"phase3-ida-range-starter-packet-test\"",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-ida-range-starter-packet_py = [_][]const u8{
    "PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST=pass",
    "Validate the current Phase 3 ida range starter packet.",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_range_dump_zig = [_][]const u8{
    "const ida_range_view = @import(\"ida_range_view\");",
    "\"clamped_ceiling_full\"",
    "\"clear_middle_window\"",
    "\"unordered_window\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_range_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_range_view.zig\"),",
    ".root_source_file = b.path(\"phase3_ida_range_dump.zig\"),",
    "\"phase3-ida-range-dump\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c = [_][]const u8{
    "#define BITMAP_BITS (BITMAP_LONGS * WORD_BITS)",
    "write_case(\"clamped_floor_partial\", floor_words, 1024, 1000, 1027, true);",
    "write_case(\"unordered_window\", clear_words, 0, 17, 12, false);",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_expected_json = [_][]const u8{
    "\"name\": \"clamped_ceiling_full\"",
    "\"id\": 3070",
    "\"name\": \"unordered_window\"",
    "\"summary\": null",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-ida-range\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_ida_range_dump.zig\"",
    "\"scripts\\zigux/check_phase3_ida_range.zig\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "`zig run scripts\\zigux/check_phase3_ida_range.zig -- --repo-root . --zig zig --cc gcc`",
    "pub const RangeSummary = struct {",
    "\"unordered_window\"",
    "\"name\": \"clamped_ceiling_full\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-ida-range-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-range-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-range-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-ida-range-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-ida-range-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-range-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-ida-range-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-ida-range-slice_md, marker);
    const text_required_markers__zigux_helpers_ida_range_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/ida/range/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_ida_range_view_zig_path);
    const text_required_markers__zigux_helpers_ida_range_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_ida_range_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_ida_range_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_ida_range_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_ida_range_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/range/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_range_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/range/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_range_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_range_starter_packet_build_zig, marker);
    const text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-ida-range-starter-packet/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-ida-range-starter-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-ida-range-starter-packet_py, marker);
    const text_required_markers__zigux_tests_phase3_ida_range_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/range/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_range_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_range_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_range_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_range_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/range/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_range_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_range_dump_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/range/phase3/ida/range/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_range_phase3_ida_range_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/range/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_range_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/range/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_range_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_range_manifest_json, marker);
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
