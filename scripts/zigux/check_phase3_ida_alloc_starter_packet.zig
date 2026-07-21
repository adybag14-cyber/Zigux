const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDA_ALLOC_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_IDA_ALLOC_STARTER_PACKET_SELF_TEST=pass";

const STARTER_BUILD_ROUTE = [_][]const u8{
    "zig build phase3-ida-alloc-starter-packet-test --build-file zigux/tests/phase3_ida_alloc_starter_packet_build.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-ida-alloc-slice_md = [_][]const u8{
    "zigux/helpers/ida_alloc_view.zig",
    "zigux/tests/phase3_ida_alloc_starter_packet.zig",
    "zigux/tests/fixtures/phase3_ida_alloc_manifest.json",
    "scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig",
    "helper-local ida allocation packet",
};

const REQUIRED_MARKERS__zigux_helpers_ida_alloc_view_zig = [_][]const u8{
    "pub const chunk_id_span: u32 = @intCast(ida_bitmap_view.bitmap_bits);",
    "pub const AllocationRange = struct {",
    "pub fn firstCandidateInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {",
    "pub fn firstFreeInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {",
    "test \"ida alloc view clamps the first candidate to the chunk floor\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_alloc_starter_packet_zig = [_][]const u8{
    "test \"ida alloc starter packet keeps the chunk-span contract explicit\" {",
    "test \"ida alloc starter packet keeps sparse allocation search explicit\" {",
    "test \"ida alloc starter packet keeps chunk-floor clamping explicit\" {",
    "test \"ida alloc starter packet keeps ceiling clamping and disjoint windows distinct\" {",
    "test \"ida alloc starter packet keeps ordered-range failure explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_ida_alloc_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/ida_alloc_view.zig\"),",
    ".root_source_file = b.path(\"phase3_ida_alloc_starter_packet.zig\"),",
    "root_module.addImport(\"ida_alloc_view\", ida_alloc_view);",
    "\"phase3-ida-alloc-starter-packet-test\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_alloc_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-ida-alloc\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_ida_alloc_starter_packet.zig\"",
    "\"zigux/tests/phase3_ida_alloc_dump.zig\"",
    "\"zig run scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig -- --self-test\"",
    "\"repo_reality_gaps\": []",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_ida_alloc_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_ida_alloc.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_ida_alloc.zig -- --repo-root . --zig zig --cc gcc",
    "zig build phase3-ida-alloc-dump --build-file zigux/tests/phase3_ida_alloc_dump_build.zig",
};

const SELF_TEST_CASES = [_][]const u8{
    "zigux/tests/fixtures/phase3_ida_alloc_manifest.json",
    "pub fn firstFreeInRange(self: AllocationView, alloc_range: AllocationRange) ?Selection {",
    "test \"ida alloc starter packet keeps sparse allocation search explicit\" {",
    "\"phase3-ida-alloc-starter-packet-test\"",
    "\"status\": \"starter_and_dump_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_starter_build_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-alloc-slice.md");
    defer allocator.free(text_starter_build_route_path);
    const text_starter_build_route = try guard.readUtf8File(io, allocator, text_starter_build_route_path);
    defer allocator.free(text_starter_build_route);
    for (STARTER_BUILD_ROUTE) |marker| try guard.requireMarker(text_starter_build_route, marker);
    const text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-alloc-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-ida-alloc-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-ida-alloc-slice_md, marker);
    const text_required_markers__zigux_helpers_ida_alloc_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/ida/alloc/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_ida_alloc_view_zig_path);
    const text_required_markers__zigux_helpers_ida_alloc_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_ida_alloc_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_ida_alloc_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_ida_alloc_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_ida_alloc_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/alloc/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_alloc_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/ida/alloc/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_ida_alloc_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_ida_alloc_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/ida/alloc/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_ida_alloc_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_ida_alloc_manifest_json, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-ida-alloc-slice.md");
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
