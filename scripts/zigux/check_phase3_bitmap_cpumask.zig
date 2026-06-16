const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_BITMAP_CPUMASK_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --self-test",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --repo-root . --cc gcc",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-bitmap-cpumask-slice_md = [_][]const u8{
    "This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.",
    "`zigux/helpers/bitmap_view.zig`",
    "`zigux/helpers/cpumask_view.zig`",
    "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
    "`zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`",
    "`scripts\\zigux/check_phase3_bitmap_cpumask.zig`",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --self-test",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --repo-root . --cc gcc",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "It does not yet claim exported ABI structs, scheduler-affinity policy, or full kernel cpumask traversal parity beyond bounded next-cpu helper walking.",
};

const REQUIRED_MARKERS__zigux_helpers_bitmap_view_zig = [_][]const u8{
    "pub const BitmapView = struct {",
    "pub fn countSetBits(self: BitmapView) usize {",
    "pub fn firstSetBit(self: BitmapView) ?usize {",
    "pub fn firstClearBit(self: BitmapView) ?usize {",
    "test \"bitmap view ignores padding bits past the declared range\" {",
};

const REQUIRED_MARKERS__zigux_helpers_cpumask_view_zig = [_][]const u8{
    "pub const CpuMaskView = struct {",
    "pub fn countPresentCpus(self: CpuMaskView) usize {",
    "pub fn firstMissingCpu(self: CpuMaskView) ?usize {",
    "pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {",
    "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig = [_][]const u8{
    "test \"bitmap starter packet keeps set-bit counting bounded to the declared range\" {",
    "test \"bitmap starter packet keeps a sparse shared bitmap reviewable\" {",
    "test \"cpumask starter packet keeps cpu membership and missing-cpu discovery explicit\" {",
    "test \"cpumask starter packet keeps subset and overlap semantics inside the bounded mask\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    ".root_source_file = b.path(\"phase3_bitmap_cpumask_starter_packet.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"cpumask_view\", cpumask_view);",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "\"Run the shared Phase 3 bitmap/cpumask starter packet\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c = [_][]const u8{
    "static size_t count_set_bits(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "static int first_set_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "static int first_clear_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "        \"      \\\"name\\\": \\\"bitmap_full_range\\\",\\n\"",
    "        \"      \\\"name\\\": \\\"cpumask_subset_overlap\\\",\\n\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json = [_][]const u8{
    "\"word_bits\": 64",
    "\"name\": \"bitmap_full_range\"",
    "\"set_count\": 67",
    "\"name\": \"cpumask_presence\"",
    "\"present_count\": 3",
    "\"base_intersects_disjoint\": false",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-bitmap-cpumask-starter-packet\"",
    "\"status\": \"helper_local_bitmap_cpumask_fixture_packet_present\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json\"",
    "\"zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --repo-root . --cc gcc\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`",
    "pub fn firstClearBit(self: BitmapView) ?usize {",
    "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
    "test \"cpumask starter packet keeps subset and overlap semantics inside the bounded mask\" {",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "        \"      \\\"name\\\": \\\"cpumask_subset_overlap\\\",\\n\"",
    "\"base_intersects_disjoint\": false",
    "\"status\": \"helper_local_bitmap_cpumask_fixture_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-bitmap-cpumask-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-bitmap-cpumask-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-bitmap-cpumask-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md, marker);
    const text_required_markers__zigux_helpers_bitmap_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/bitmap/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_bitmap_view_zig_path);
    const text_required_markers__zigux_helpers_bitmap_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_bitmap_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_bitmap_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_bitmap_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_bitmap_view_zig, marker);
    const text_required_markers__zigux_helpers_cpumask_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/cpumask/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_cpumask_view_zig_path);
    const text_required_markers__zigux_helpers_cpumask_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_cpumask_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_cpumask_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_cpumask_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_cpumask_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/bitmap/cpumask/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/bitmap/cpumask/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/bitmap/cpumask/phase3/bitmap/cpumask/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_phase3_bitmap_cpumask_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/bitmap/cpumask/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/bitmap/cpumask/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_bitmap_cpumask_manifest_json, marker);
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
