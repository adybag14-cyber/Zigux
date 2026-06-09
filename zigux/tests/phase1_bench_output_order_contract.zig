const std = @import("std");

const bench_source = @embedFile("phase1_bench.zig");
const expectations_json = @embedFile("fixtures/phase1_bench_expectations.json");

const expected_iterations = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const expected_checksums = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

fn requireMarkerAfter(text: []const u8, cursor: usize, marker: []const u8) !usize {
    if (std.mem.indexOfPos(u8, text, cursor, marker)) |index| {
        return index + marker.len;
    }
    if (std.mem.indexOf(u8, text, marker) != null) {
        return error.OutOfOrderOutputKey;
    }
    return error.MissingMarker;
}

fn requireSourcePrintAfter(text: []const u8, cursor: usize, key: []const u8) !usize {
    var marker_buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(
        &marker_buffer,
        "\"{s}={{d}}\\n\"",
        .{key},
    );
    return requireMarkerAfter(text, cursor, marker);
}

fn requireQuotedKeyAfter(text: []const u8, cursor: usize, key: []const u8) !usize {
    var marker_buffer: [128]u8 = undefined;
    const marker = try std.fmt.bufPrint(
        &marker_buffer,
        "\"{s}\"",
        .{key},
    );
    return requireMarkerAfter(text, cursor, marker);
}

fn validateBenchSourceOutputOrder(text: []const u8) !void {
    var cursor = try requireMarkerAfter(text, 0, "\"PHASE1_BENCH=pass\\n\"");
    for (expected_iterations) |key| {
        cursor = try requireSourcePrintAfter(text, cursor, key);
    }
    for (expected_checksums) |key| {
        cursor = try requireSourcePrintAfter(text, cursor, key);
    }
}

fn validateExpectationsRosterOrder(text: []const u8) !void {
    var cursor = try requireMarkerAfter(text, 0, "\"status\": \"pass\"");
    cursor = try requireMarkerAfter(text, cursor, "\"iterations\"");
    for (expected_iterations) |key| {
        cursor = try requireQuotedKeyAfter(text, cursor, key);
    }
    cursor = try requireMarkerAfter(text, cursor, "\"checksums\"");
    for (expected_checksums) |key| {
        cursor = try requireQuotedKeyAfter(text, cursor, key);
    }
    cursor = try requireMarkerAfter(text, cursor, "\"exact_checksums\"");
    for (expected_checksums) |key| {
        cursor = try requireQuotedKeyAfter(text, cursor, key);
    }
}

fn validateCheckerConstantOrder(text: []const u8) !void {
    var cursor = try requireMarkerAfter(text, 0, "EXPECTED_ITERATIONS = {");
    for (expected_iterations) |key| {
        cursor = try requireQuotedKeyAfter(text, cursor, key);
    }
    cursor = try requireMarkerAfter(text, cursor, "EXPECTED_CHECKSUMS = [");
    for (expected_checksums) |key| {
        cursor = try requireQuotedKeyAfter(text, cursor, key);
    }
}

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase1 bench source prints status iterations then checksums" {
    try validateBenchSourceOutputOrder(bench_source);
}

test "phase1 bench fixture keeps the same ordered output roster" {
    try validateExpectationsRosterOrder(expectations_json);
}

test "phase1 bench checker constants keep the same ordered roster" {
    const bench_checker = try readFileAlloc(
        std.testing.allocator,
        "scripts/zigux/check-phase1-bench.py",
        128 * 1024,
    );
    defer std.testing.allocator.free(bench_checker);

    try validateCheckerConstantOrder(bench_checker);
}

test "output order guard rejects checksum before iteration drift" {
    const reordered_source =
        \\try stdout_writer.interface.print("PHASE1_BENCH=pass\n", .{});
        \\try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\n", .{checksum});
        \\try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_STRING_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\n", .{iterations});
        \\try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\n", .{iterations});
    ;

    try std.testing.expectError(
        error.OutOfOrderOutputKey,
        validateBenchSourceOutputOrder(reordered_source),
    );
}
