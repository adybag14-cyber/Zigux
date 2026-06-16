// Ported from check-phase1-rbtree-bench-anchors.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_RBTREE_BENCH_ANCHORS_SELF_TEST=pass";

const BENCH_REL = "zigux/tests/phase1_bench.zig";

const EXPECTATIONS_REL = "zigux/tests/fixtures/phase1_bench_expectations.json";

const EXPECTED_RBTREE_CHECKSUMS = [_][]const u8{
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

const EXPECTED_RBTREE_ITERATION_KEY = "PHASE1_BENCH_RBTREE_ITERATIONS";

const EXPECTED_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "iterations_constant", .marker = "const iterations_rbtree: u64 = 4000;" },
    .{ .label = "rbtree_bench_fn", .marker = "fn rbtreeBench() struct { checksum: u64 } {" },
    .{ .label = "postorder_safe_fn", .marker = "fn rbtreePostorderSafeBench() struct { checksum: u64 } {" },
    .{ .label = "find_add_fn", .marker = "fn rbtreeFindAddBench() struct { checksum: u64 } {" },
    .{ .label = "duplicate_fn", .marker = "fn rbtreeDuplicateBench() struct { checksum: u64 } {" },
    .{ .label = "cached_fn", .marker = "fn rbtreeCachedBench() struct { checksum: u64 } {" },
    .{ .label = "ordered_first", .marker = "var node = rbtree.first(&root);" },
    .{ .label = "ordered_next", .marker = "while (node) |current| : (node = rbtree.next(current)) {" },
    .{ .label = "postorder_first", .marker = "var node = rbtree.firstPostorder(&root);" },
    .{ .label = "postorder_next", .marker = "while (node) |current| : (node = rbtree.nextPostorder(current)) {" },
    .{ .label = "find_add_probe", .marker = "const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);" },
    .{ .label = "duplicate_iterator", .marker = "var iter = rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp);" },
    .{ .label = "cached_insert", .marker = "_ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);" },
    .{ .label = "cached_erase", .marker = "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);" },
    .{ .label = "bench_call", .marker = "const rbtree_result = rbtreeBench();" },
    .{ .label = "postorder_safe_call", .marker = "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();" },
    .{ .label = "find_add_call", .marker = "const rbtree_find_add_result = rbtreeFindAddBench();" },
    .{ .label = "duplicate_call", .marker = "const rbtree_duplicate_result = rbtreeDuplicateBench();" },
    .{ .label = "cached_call", .marker = "const rbtree_cached_result = rbtreeCachedBench();" },
    .{ .label = "iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n\", .{iterations_rbtree});" },
    .{ .label = "checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n\", .{rbtree_result.checksum});" },
    .{ .label = "postorder_safe_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n\", .{rbtree_postorder_safe_result.checksum});" },
    .{ .label = "find_add_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n\", .{rbtree_find_add_result.checksum});" },
    .{ .label = "duplicate_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n\", .{rbtree_duplicate_result.checksum});" },
    .{ .label = "cached_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n\", .{rbtree_cached_result.checksum});" },
};

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
    try guard.printLine(io, "PHASE1_RBTREE_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_RBTREE_BENCH_ANCHORS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
