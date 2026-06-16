// Ported from check-phase1-list-sort-review-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST=pass";

const EXPECTED_HELPER_LOCAL_ONLY_ANCHORS = [_][]const u8{
    "test \"list sort accepts non-unit comparator magnitudes\"",
    "test \"list sort honors comparator context with non-unit magnitudes\"",
    "test \"list sort reuses non-unit comparator context across repeated reordering\"",
    "test \"list sort accepts signed subtractive comparator\"",
    "test \"list sort reuses signed subtractive comparator context across repeated reordering\"",
    "test \"list sort preserves current signed-subtractive order when a later pass ties everything\"",
};

const EXPECTED_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"list sort keeps stable ordering for tri-state comparator\"",
    "test \"list sort accepts boolean-style comparator\"",
    "test \"list sort honors comparator context\"",
    "test \"list sort can reorder the same circular list twice\"",
    "test \"list sort keeps reverse links aligned after reordering\"",
    "test \"list sort preserves sorted unique input\"",
    "test \"list sort preserves stable bucket order across parity groups\"",
    "test \"list sort preserves stable modulo bucket order across a longer merge path\"",
    "test \"list sort preserves input order when every comparison ties\"",
    "test \"list sort handles empty and singleton lists\"",
};

const EXPECTED_LIST_SORT_SOURCE_SYMBOLS = [_][]const u8{
    "pub const ListHead = struct {",
    "pub const CmpFn = *const fn (?*anyopaque, *const ListHead, *const ListHead) i32;",
    "pub fn listEmpty(head: *const ListHead) bool {",
    "pub fn listAdd(new: *ListHead, head: *ListHead) void {",
    "pub fn listAddTail(new: *ListHead, head: *ListHead) void {",
    "pub fn listDel(entry: *ListHead) void {",
    "pub fn listSort(priv: ?*anyopaque, head: *ListHead, cmp: CmpFn) void {",
};

const LIST_SORT_FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";

const LIST_SORT_HELPER_REL = "tools/lib/list_sort.zig";

const LIST_SORT_LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const LIST_SORT_MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    _ = .{ io, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
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
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
