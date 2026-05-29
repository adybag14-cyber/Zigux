const std = @import("std");

const BenchMetric = enum {
    bitmap_weight,
    bitmap_window,
    find_next_bit,
    find_bit_edge,
    string,
    hweight,
    list_sort,
    rbtree,
};

const MetricPair = struct {
    metric: BenchMetric,
    iteration_key: []const u8,
    checksum_key: []const u8,
};

const metric_pairs = [_]MetricPair{
    .{
        .metric = .bitmap_weight,
        .iteration_key = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    },
    .{
        .metric = .bitmap_window,
        .iteration_key = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    },
    .{
        .metric = .find_next_bit,
        .iteration_key = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    },
    .{
        .metric = .find_bit_edge,
        .iteration_key = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    },
    .{
        .metric = .string,
        .iteration_key = "PHASE1_BENCH_STRING_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_STRING_CHECKSUM",
    },
    .{
        .metric = .hweight,
        .iteration_key = "PHASE1_BENCH_HWEIGHT_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    },
    .{
        .metric = .list_sort,
        .iteration_key = "PHASE1_BENCH_LIST_SORT_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    },
    .{
        .metric = .rbtree,
        .iteration_key = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_key = "PHASE1_BENCH_RBTREE_CHECKSUM",
    },
};

const rbtree_detail_keys = [_][]const u8{
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

const ContractError = error{
    EmptyLine,
    MalformedLine,
    MissingPassMarker,
    UnexpectedPassValue,
    DuplicateKey,
    UnknownMetricKey,
    MissingIterationKey,
    MissingChecksumKey,
    ChecksumBeforeIteration,
    MissingRbtreeAggregateBeforeDetail,
    MissingRbtreeDetailKey,
};

const SeenMetric = struct {
    iteration_line: ?usize = null,
    checksum_line: ?usize = null,
};

const Seen = struct {
    pass_line: ?usize = null,
    metrics: [metric_pairs.len]SeenMetric = [_]SeenMetric{.{}} ** metric_pairs.len,
    rbtree_detail_lines: [rbtree_detail_keys.len]?usize = [_]?usize{null} ** rbtree_detail_keys.len,
};

fn metricIndex(metric: BenchMetric) usize {
    return @intFromEnum(metric);
}

fn recordOptionalLine(slot: *?usize, line_no: usize) ContractError!void {
    if (slot.* != null) return error.DuplicateKey;
    slot.* = line_no;
}

fn recordKey(seen: *Seen, key: []const u8, line_no: usize) ContractError!void {
    if (std.mem.eql(u8, key, "PHASE1_BENCH")) {
        try recordOptionalLine(&seen.pass_line, line_no);
        return;
    }

    inline for (metric_pairs) |pair| {
        const idx = metricIndex(pair.metric);
        if (std.mem.eql(u8, key, pair.iteration_key)) {
            try recordOptionalLine(&seen.metrics[idx].iteration_line, line_no);
            return;
        }
        if (std.mem.eql(u8, key, pair.checksum_key)) {
            try recordOptionalLine(&seen.metrics[idx].checksum_line, line_no);
            return;
        }
    }

    inline for (rbtree_detail_keys, 0..) |detail_key, idx| {
        if (std.mem.eql(u8, key, detail_key)) {
            try recordOptionalLine(&seen.rbtree_detail_lines[idx], line_no);
            return;
        }
    }

    return error.UnknownMetricKey;
}

fn validateBenchOutput(output: []const u8) ContractError!void {
    var seen = Seen{};
    var lines = std.mem.splitScalar(u8, output, '\n');
    var line_no: usize = 0;

    while (lines.next()) |line| {
        if (line.len == 0) continue;
        line_no += 1;
        const equals_index = std.mem.indexOfScalar(u8, line, '=') orelse return error.MalformedLine;
        if (equals_index == 0 or equals_index == line.len - 1) return error.MalformedLine;
        const key = line[0..equals_index];
        const value = line[equals_index + 1 ..];
        if (std.mem.eql(u8, key, "PHASE1_BENCH") and !std.mem.eql(u8, value, "pass")) {
            return error.UnexpectedPassValue;
        }
        try recordKey(&seen, key, line_no);
    }

    if (line_no == 0) return error.EmptyLine;
    if (seen.pass_line == null) return error.MissingPassMarker;

    inline for (metric_pairs) |pair| {
        const metric = seen.metrics[metricIndex(pair.metric)];
        const iteration_line = metric.iteration_line orelse return error.MissingIterationKey;
        const checksum_line = metric.checksum_line orelse return error.MissingChecksumKey;
        if (checksum_line <= iteration_line) return error.ChecksumBeforeIteration;
    }

    const rbtree_checksum_line = seen.metrics[metricIndex(.rbtree)].checksum_line orelse unreachable;
    inline for (seen.rbtree_detail_lines) |detail_line| {
        const line = detail_line orelse return error.MissingRbtreeDetailKey;
        if (line <= rbtree_checksum_line) return error.MissingRbtreeAggregateBeforeDetail;
    }
}

const live_bench_shape =
    \\PHASE1_BENCH=pass
    \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
    \\PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000
    \\PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000
    \\PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=2680000
    \\PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000
    \\PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM=59685
    \\PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000
    \\PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM=21500000
    \\PHASE1_BENCH_STRING_ITERATIONS=40000
    \\PHASE1_BENCH_STRING_CHECKSUM=12840000
    \\PHASE1_BENCH_HWEIGHT_ITERATIONS=100000
    \\PHASE1_BENCH_HWEIGHT_CHECKSUM=13900000
    \\PHASE1_BENCH_LIST_SORT_ITERATIONS=1000
    \\PHASE1_BENCH_LIST_SORT_CHECKSUM=69000
    \\PHASE1_BENCH_RBTREE_ITERATIONS=4000
    \\PHASE1_BENCH_RBTREE_CHECKSUM=122000
    \\PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM=12000
    \\PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM=36000
    \\PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=32000
    \\PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=42000
;

test "lane17 phase1 bench live-check output contract accepts complete shape" {
    try validateBenchOutput(live_bench_shape);
}

test "lane17 phase1 bench live-check output contract rejects missing pass marker" {
    try std.testing.expectError(
        error.MissingPassMarker,
        validateBenchOutput("PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000\n"),
    );
}

test "lane17 phase1 bench live-check output contract rejects duplicate metrics" {
    const duplicate =
        \\PHASE1_BENCH=pass
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
    ;
    try std.testing.expectError(error.DuplicateKey, validateBenchOutput(duplicate));
}

test "lane17 phase1 bench live-check output contract rejects checksum before iteration" {
    const reordered =
        \\PHASE1_BENCH=pass
        \\PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
    ;
    try std.testing.expectError(error.ChecksumBeforeIteration, validateBenchOutput(reordered));
}

test "lane17 phase1 bench live-check output contract rejects unknown metric keys" {
    const unknown =
        \\PHASE1_BENCH=pass
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
        \\PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000
        \\PHASE1_BENCH_UNTRACKED_CHECKSUM=1
    ;
    try std.testing.expectError(error.UnknownMetricKey, validateBenchOutput(unknown));
}

test "lane17 phase1 bench live-check output contract requires rbtree detail split" {
    const missing_detail =
        \\PHASE1_BENCH=pass
        \\PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000
        \\PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=2260000
        \\PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000
        \\PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=2680000
        \\PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000
        \\PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM=59685
        \\PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000
        \\PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM=21500000
        \\PHASE1_BENCH_STRING_ITERATIONS=40000
        \\PHASE1_BENCH_STRING_CHECKSUM=12840000
        \\PHASE1_BENCH_HWEIGHT_ITERATIONS=100000
        \\PHASE1_BENCH_HWEIGHT_CHECKSUM=13900000
        \\PHASE1_BENCH_LIST_SORT_ITERATIONS=1000
        \\PHASE1_BENCH_LIST_SORT_CHECKSUM=69000
        \\PHASE1_BENCH_RBTREE_ITERATIONS=4000
        \\PHASE1_BENCH_RBTREE_CHECKSUM=122000
    ;
    try std.testing.expectError(error.MissingRbtreeDetailKey, validateBenchOutput(missing_detail));
}
