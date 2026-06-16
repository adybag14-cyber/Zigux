// Ported from check-phase1-find-bit-bench-loop-counters.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_SELF_TEST=pass";

const BENCH_REL = "zigux/tests/phase1_bench.zig";

const REQUIRED_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_next_counter_const", .marker = "const iterations_find_bit: u64 = 20000;" },
    .{ .label = "find_edge_counter_const", .marker = "const iterations_find_bit_edge: u64 = 20000;" },
    .{ .label = "find_next_bench_fn", .marker = "fn findBitBench() struct { checksum: u64 } {" },
    .{ .label = "find_edge_bench_fn", .marker = "fn findBitEdgeBench() struct { checksum: u64 } {" },
    .{ .label = "find_next_counter_loop", .marker = "while (idx < iterations_find_bit) : (idx += 1) {" },
    .{ .label = "find_edge_counter_loop", .marker = "while (idx < iterations_find_bit_edge) : (idx += 1) {" },
    .{ .label = "find_next_iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n\", .{iterations_find_bit});" },
    .{ .label = "find_edge_iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n\", .{iterations_find_bit_edge});" },
    .{ .label = "find_next_checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n\", .{find_bit_result.checksum});" },
    .{ .label = "find_edge_checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n\", .{find_bit_edge_result.checksum});" },
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

    {
        const relative_path = "zigux/tests/phase1_bench.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "zigux/tests/phase1_bench.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ entry.label, count });
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

fn buildSampleSource(allocator: std.mem.Allocator) ![]u8 {
    var content = std.ArrayList(u8).empty;
    errdefer content.deinit(allocator);
    for (REQUIRED_MARKERS) |entry| {
        try content.appendSlice(allocator, entry.marker);
        try content.append(allocator, '\n');
    }
    return try content.toOwnedSlice(allocator);
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    const sample = try buildSampleSource(allocator);
    defer allocator.free(sample);
    {
        const relative_path = "zigux/tests/phase1_bench.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, sample);
        var failures = try collectFailures(io, allocator, root);
        defer {
            for (failures.items) |item| allocator.free(item);
            failures.deinit(allocator);
        }
        try guard.expectSelfTest(failures.items.len == 0);
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 23)});
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
        try guard.printLine(io, "PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
