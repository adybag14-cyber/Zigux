const std = @import("std");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const Phase1Marker = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_guard_pairs = [_]Phase1Marker{
    .{
        .name = "      - name: Self-test current Phase 1 route summary checker",
        .run = "        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 route summary packet",
        .run = "        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench checker",
        .run = "        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench packet",
        .run = "        run: zig run scripts/zigux/check_phase1_bench.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 bench live-check workflow guard",
        .run = "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 bench live-check workflow guard packet",
        .run = "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 find-bit bench anchor checker",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 find-bit bench anchor packet",
        .run = "        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 shared reminder checker",
        .run = "        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 shared reminder packet",
        .run = "        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig",
    },
    .{
        .name = "      - name: Self-test current Phase 1 closure validator",
        .run = "        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test",
    },
    .{
        .name = "      - name: Check current Phase 1 closure packet",
        .run = "        run: zig run scripts/zigux/validate_phase1_closure.zig",
    },
};

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, needle)) count += 1;
    }
    return count;
}

fn indexOfExactLine(haystack: []const u8, needle: []const u8) ?usize {
    var start: usize = 0;
    while (start <= haystack.len) {
        const end = std.mem.indexOfScalarPos(u8, haystack, start, '\n') orelse haystack.len;
        if (std.mem.eql(u8, haystack[start..end], needle)) return start;
        if (end == haystack.len) break;
        start = end + 1;
    }
    return null;
}

fn requireOnce(haystack: []const u8, needle: []const u8) WorkflowError!usize {
    const first = indexOfExactLine(haystack, needle) orelse return error.MissingMarker;
    if (countExactLines(haystack, needle) != 1) return error.DuplicateMarker;
    return first;
}

fn requireAfter(previous: *?usize, haystack: []const u8, needle: []const u8) WorkflowError!void {
    const index = try requireOnce(haystack, needle);
    if (previous.*) |previous_index| {
        if (index <= previous_index) return error.ReorderedMarker;
    }
    previous.* = index;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) WorkflowError!void {
    if (indexOfExactLine(haystack, needle) != null) return error.StaleMarker;
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(1024 * 1024),
    );
}

fn validatePhase1WorkflowGuardPairs(workflow: []const u8) WorkflowError!void {
    var previous: ?usize = null;
    for (phase1_guard_pairs) |marker| {
        try requireAfter(&previous, workflow, marker.name);
        try requireAfter(&previous, workflow, marker.run);
    }

    try requireAfter(&previous, workflow, "      - name: Self-test current Phase 3 interop packet");
    try requireAfter(&previous, workflow, "        run: zig run scripts/zigux/validate_phase3_selftest.zig");
    try requireAfter(&previous, workflow, "      - name: Check current Phase 3 interop packet");
    try requireAfter(&previous, workflow, "        run: zig run scripts/zigux/run_phase3_checks.zig");
    try requireAfter(&previous, workflow, "      - name: Run current Phase 3 shared tests-root packet");
    try requireAfter(&previous, workflow, "        run: zig build phase3-test --build-file zigux/tests/build.zig");
    try requireAfter(&previous, workflow, "      - name: Run current Phase 3 ABI dump replay");
    try requireAfter(&previous, workflow, "        run: zig build phase3-dump --build-file zigux/tests/build.zig");
    try requireAfter(&previous, workflow, "      - name: Run current Phase 1 shared tests-root smoke");
    try requireAfter(&previous, workflow, "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try requireAfter(&previous, workflow, "      - name: Self-test current Phase 4 repo-reality warning checker");

    try requireAbsent(workflow, "        run: zig run scripts/zigux/check_phase1_bench.zig -- --allow-missing");
    try requireAbsent(workflow, "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --allow-missing");
    try requireAbsent(workflow, "        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --root");
}

test "current bootstrap workflow keeps phase1 guard pairs unique and ordered" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validatePhase1WorkflowGuardPairs(workflow);
}

test "contract rejects missing live bench packet check" {
    const workflow =
        \\      - name: Self-test current Phase 1 route summary checker
        \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test
        \\      - name: Check current Phase 1 route summary packet
        \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase1WorkflowGuardPairs(workflow));
}

test "contract rejects duplicated phase1 workflow guard commands" {
    const current_workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(current_workflow);

    const workflow = try std.mem.concat(
        std.testing.allocator,
        u8,
        &.{
            current_workflow,
            "\n        run: zig run scripts/zigux/check_phase1_bench.zig\n",
        },
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expectError(error.DuplicateMarker, validatePhase1WorkflowGuardPairs(workflow));
}

test "contract rejects reordered phase1 live-check workflow guard" {
    const workflow =
        \\      - name: Self-test current Phase 1 route summary checker
        \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test
        \\      - name: Check current Phase 1 route summary packet
        \\        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test
        \\      - name: Check current Phase 1 bench packet
        \\        run: zig run scripts/zigux/check_phase1_bench.zig
        \\      - name: Check current Phase 1 bench live-check workflow guard packet
        \\        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig
        \\      - name: Self-test current Phase 1 bench live-check workflow guard
        \\        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase1WorkflowGuardPairs(workflow));
}

test "contract rejects stale optional workflow command variants" {
    const current_workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(current_workflow);

    const workflow = try std.mem.concat(
        std.testing.allocator,
        u8,
        &.{
            current_workflow,
            "\n        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --allow-missing\n",
        },
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expectError(error.StaleMarker, validatePhase1WorkflowGuardPairs(workflow));
}
