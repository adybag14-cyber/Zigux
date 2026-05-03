pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
};

pub const query_count = 32;

pub const perf_cases = [_]PerfCase{
    .{ .label = "256", .len = 256, .reps = 2_000 },
    .{ .label = "4096", .len = 4096, .reps = 500 },
    .{ .label = "65536", .len = 65536, .reps = 64 },
};

pub fn seedDeterministicQueries(
    len: usize,
    values: []const u32,
    queries: *[query_count]u32,
    expected_hits: *[query_count]bool,
) void {
    const quarter = len / 4;
    const middle = len / 2;
    const last = len - 1;
    const deterministic_pairs = [_]struct {
        query: u32,
        hit: bool,
    }{
        .{ .query = values[0], .hit = true },
        .{ .query = values[0] + 1, .hit = false },
        .{ .query = values[quarter], .hit = true },
        .{ .query = values[quarter] + 1, .hit = false },
        .{ .query = values[middle], .hit = true },
        .{ .query = values[middle] + 1, .hit = false },
        .{ .query = values[last], .hit = true },
        .{ .query = values[last] + 1, .hit = false },
    };

    for (deterministic_pairs, 0..) |pair, idx| {
        queries[idx] = pair.query;
        expected_hits[idx] = pair.hit;
    }
}
