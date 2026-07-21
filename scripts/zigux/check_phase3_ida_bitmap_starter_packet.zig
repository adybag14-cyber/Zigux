const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDA_BITMAP_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST=pass";

const STARTER_BUILD_ROUTE = [_][]const u8{
    "zig build phase3-ida-bitmap-starter-packet-test --build-file zigux/tests/phase3_ida_bitmap_starter_packet_build.zig",
};

const CHECKER_ROUTE = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_ida_bitmap_starter_packet.zig -- --repo-root .",
};

const SELF_TEST_ROUTE = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_ida_bitmap_starter_packet.zig -- --self-test",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-ida-bitmap-slice_md = [_][]const u8{
    "zigux/helpers/ida_bitmap_view.zig",
    "zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_ida_bitmap_starter_packet.zig",
    "fixed 128-byte IDA bitmap chunk",
    "The landed `ida_bitmap` helper-local starter packet is real repo evidence",
};

const REQUIRED_MARKERS__zigux_helpers_ida_bitmap_view_zig = [_][]const u8{
    "pub const chunk_size_bytes: usize = 128;",
    "pub const bitmap_bits: usize = bitmap_longs * word_bits;",
    "pub fn isFull(self: BitmapView) bool {",
    "pub fn weight(self: BitmapView) usize {",
    "pub fn firstZero(self: BitmapView) ?usize {",
    "test \"ida bitmap constants keep the fixed chunk geometry\" {",
    "test \"full ida bitmap chunk reports no zero bits left\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_zig = [_][]const u8{
    "test \"ida bitmap starter packet keeps the fixed chunk geometry explicit\" {",
    "test \"ida bitmap starter packet keeps an empty chunk reviewable\" {",
    "test \"ida bitmap starter packet keeps sparse words explicit across chunk boundaries\" {",
    "test \"ida bitmap starter packet keeps full chunks and first-zero exhaustion distinct\" {",
    "test \"ida bitmap starter packet keeps the first clear position visible inside a partially used word\" {",
    "try testing.expectEqual(@as(?usize, 2), view.firstZero());",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_bitmap_view.zig\"),",
    ".root_source_file = b.path(\"phase3_ida_bitmap_starter_packet.zig\"),",
    "root_module.addImport(\"ida_bitmap_view\", ida_bitmap_view);",
    "\"phase3-ida-bitmap-starter-packet-test\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-ida-bitmap-starter-packet\"",
    "\"status\": \"starter_packet_present\"",
    "\"Documentation/zigux/phase3-ida-bitmap-slice.md\"",
    "\"zigux/helpers/ida_bitmap_view.zig\"",
    "\"zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json\"",
    "\"repo_reality_gaps\": []",
    "\"next_safe_step\": \"keep the helper-local ida bitmap packet honest with manifest-backed replay before widening into broader ida allocation or range semantics\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "SELF_TEST_ROUTE",
    "CHECKER_ROUTE",
    "STARTER_BUILD_ROUTE",
};

const SELF_TEST_CASES = [_][]const u8{
    "zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json",
    "\"{CHECKER_ROUTE}\"",
    "pub fn firstZero(self: BitmapView) ?usize {",
    "test \"ida bitmap starter packet keeps sparse words explicit across chunk boundaries\" {",
    "\"phase3-ida-bitmap-starter-packet-test\"",
    "\"status\": \"starter_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_starter_build_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-bitmap-slice.md");
    defer allocator.free(text_starter_build_route_path);
    const text_starter_build_route = try guard.readUtf8File(io, allocator, text_starter_build_route_path);
    defer allocator.free(text_starter_build_route);
    for (STARTER_BUILD_ROUTE) |marker| try guard.requireMarker(text_starter_build_route, marker);
    const text_checker_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-bitmap-slice.md");
    defer allocator.free(text_checker_route_path);
    const text_checker_route = try guard.readUtf8File(io, allocator, text_checker_route_path);
    defer allocator.free(text_checker_route);
    for (CHECKER_ROUTE) |marker| try guard.requireMarker(text_checker_route, marker);
    const text_self_test_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-bitmap-slice.md");
    defer allocator.free(text_self_test_route_path);
    const text_self_test_route = try guard.readUtf8File(io, allocator, text_self_test_route_path);
    defer allocator.free(text_self_test_route);
    for (SELF_TEST_ROUTE) |marker| try guard.requireMarker(text_self_test_route, marker);
    const text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-bitmap-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-ida-bitmap-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-ida-bitmap-slice_md, marker);
    const text_required_markers__zigux_helpers_ida_bitmap_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/ida/bitmap/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_ida_bitmap_view_zig_path);
    const text_required_markers__zigux_helpers_ida_bitmap_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_ida_bitmap_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_ida_bitmap_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_ida_bitmap_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_ida_bitmap_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/bitmap/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/bitmap/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/bitmap/starter/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_bitmap_starter_packet_manifest_json, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
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
