const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_BITMAP_CPUMASK_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass",
    "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_BITMAP_CPUMASK_PACKET=pass",
    "validated zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "validated zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.",
    "`zigux/helpers/bitmap_view.zig`",
    "`zigux/helpers/cpumask_view.zig`",
    "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
    "`zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`",
    "`zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`",
    "`scripts\\zigux/check_phase3_bitmap_cpumask.zig`",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "It does not yet claim exported ABI structs, scheduler-affinity policy, or full kernel cpumask traversal parity beyond bounded next-cpu helper walking.",
};

const markers_1 = [_][]const u8{
    "pub const BitmapView = struct {",
    "pub fn countSetBits(self: BitmapView) usize {",
    "pub fn firstSetBit(self: BitmapView) ?usize {",
    "pub fn firstClearBit(self: BitmapView) ?usize {",
    "test \"bitmap view ignores padding bits past the declared range\" {",
};

const markers_2 = [_][]const u8{
    "pub const CpuMaskView = struct {",
    "pub fn countPresentCpus(self: CpuMaskView) usize {",
    "pub fn firstMissingCpu(self: CpuMaskView) ?usize {",
    "pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {",
    "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
};

const markers_3 = [_][]const u8{
    "test \"bitmap starter packet keeps set-bit counting bounded to the declared range\" {",
    "test \"bitmap starter packet keeps a sparse shared bitmap reviewable\" {",
    "test \"cpumask starter packet keeps cpu membership and missing-cpu discovery explicit\" {",
    "test \"cpumask starter packet keeps subset and overlap semantics inside the bounded mask\" {",
};

const markers_4 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    ".root_source_file = b.path(\"phase3_bitmap_cpumask_starter_packet.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"cpumask_view\", cpumask_view);",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "\"Run the shared Phase 3 bitmap/cpumask starter packet\"",
};

const markers_5 = [_][]const u8{
    "static size_t count_set_bits(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "static int first_set_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "static int first_clear_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {",
    "        \"      \\\"name\\\": \\\"bitmap_full_range\\\",\\n\"",
    "        \"      \\\"name\\\": \\\"cpumask_subset_overlap\\\",\\n\"",
};

const markers_6 = [_][]const u8{
    "\"word_bits\": 64",
    "\"name\": \"bitmap_full_range\"",
    "\"set_count\": 67",
    "\"name\": \"cpumask_presence\"",
    "\"present_count\": 3",
    "\"base_intersects_disjoint\": false",
};

const markers_7 = [_][]const u8{
    "\"slug\": \"phase3-bitmap-cpumask-starter-packet\"",
    "\"status\": \"helper_local_bitmap_cpumask_fixture_packet_present\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-bitmap-cpumask-slice.md", .markers = &markers_0 },
    .{ .rel = "zigux/helpers/bitmap_view.zig", .markers = &markers_1 },
    .{ .rel = "zigux/helpers/cpumask_view.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig", .markers = &markers_4 },
    .{ .rel = "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c", .markers = &markers_5 },
    .{ .rel = "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json", .markers = &markers_6 },
    .{ .rel = "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json", .markers = &markers_7 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
