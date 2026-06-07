const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const expected_ladder = [_]Step{
    .{
        .name = "Check current Phase 2 closure packet",
        .run = "python3 scripts/zigux/validate-phase2-closure.py",
    },
    .{
        .name = "Self-test current Phase 1 direct-owner checker",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "Self-test current Phase 1 route summary checker",
        .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "Check current Phase 1 route summary packet",
        .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "Self-test current Phase 1 bench checker",
        .run = "python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench packet",
        .run = "python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .name = "Self-test current Phase 1 bench live-check workflow guard",
        .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bench live-check workflow guard packet",
        .run = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit bench anchor checker",
        .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit bench anchor packet",
        .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 shared reminder checker",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 shared reminder packet",
        .run = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 closure validator",
        .run = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "Check current Phase 1 closure packet",
        .run = "python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .name = "Self-test current Phase 3 interop packet",
        .run = "python3 scripts/zigux/validate_phase3_selftest.py",
    },
};

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn stepBlock(workflow: []const u8, name: []const u8) ![]const u8 {
    const marker = try std.fmt.allocPrint(std.testing.allocator, "- name: {s}", .{name});
    defer std.testing.allocator.free(marker);

    const count = countOccurrences(workflow, marker);
    if (count == 0) return error.MissingStep;
    if (count != 1) return error.DuplicateStep;

    const start = std.mem.indexOf(u8, workflow, marker).?;
    const rest = workflow[start + marker.len ..];
    const relative_end = std.mem.indexOf(u8, rest, "\n      - name:") orelse rest.len;
    return workflow[start .. start + marker.len + relative_end];
}

fn stepIndex(workflow: []const u8, step: Step) !usize {
    const block = try stepBlock(workflow, step.name);
    if (std.mem.indexOf(u8, block, step.run) == null) return error.WrongRun;
    return @intFromPtr(block.ptr) - @intFromPtr(workflow.ptr);
}

fn validateWorkflow(workflow: []const u8) !void {
    var previous: ?usize = null;
    for (expected_ladder) |step| {
        const current = try stepIndex(workflow, step);
        if (previous) |prev| {
            if (current <= prev) return error.OutOfOrder;
        }
        previous = current;
    }

    if (std.mem.indexOf(u8, workflow, "make -C zigux phase1-bench") != null) {
        return error.StalePhase1BenchMakeRoute;
    }
    if (std.mem.indexOf(u8, workflow, "make -C zigux phase1") != null) {
        return error.StalePhase1AggregateMakeRoute;
    }
}

const valid_ladder =
    \\      - name: Check current Phase 2 closure packet
    \\        run: python3 scripts/zigux/validate-phase2-closure.py
    \\      - name: Self-test current Phase 1 direct-owner checker
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    \\      - name: Check current Phase 1 direct-owner markers
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
    \\      - name: Self-test current Phase 1 route summary checker
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
    \\      - name: Check current Phase 1 route summary packet
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
    \\      - name: Self-test current Phase 1 bench live-check workflow guard
    \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test
    \\      - name: Check current Phase 1 bench live-check workflow guard packet
    \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    \\      - name: Self-test current Phase 1 shared reminder checker
    \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
    \\      - name: Check current Phase 1 shared reminder packet
    \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
    \\      - name: Self-test current Phase 1 closure validator
    \\        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
    \\      - name: Check current Phase 1 closure packet
    \\        run: python3 scripts/zigux/validate-phase1-closure.py
    \\      - name: Self-test current Phase 3 interop packet
    \\        run: python3 scripts/zigux/validate_phase3_selftest.py
;

test "zigux bootstrap keeps the Phase 1 bench ladder between closure and Phase 3" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try validateWorkflow(workflow);
}

test "contract fails closed on missing duplicate or stale bench workflow markers" {
    const duplicate =
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;
    try std.testing.expectError(error.DuplicateStep, validateWorkflow(duplicate));

    const stale_route = valid_ladder ++
        \\      - name: Historical Phase 1 bench make route
        \\        run: make -C zigux phase1-bench
    ;
    try std.testing.expectError(error.StalePhase1BenchMakeRoute, validateWorkflow(stale_route));

    const missing_run =
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
    ;
    try std.testing.expectError(error.MissingStep, validateWorkflow(missing_run));
}

test "contract rejects stale Phase 1 aggregate make route" {
    const stale_aggregate = valid_ladder ++
        \\      - name: Historical Phase 1 aggregate make route
        \\        run: make -C zigux phase1
    ;

    try std.testing.expectError(error.StalePhase1AggregateMakeRoute, validateWorkflow(stale_aggregate));
}

test "contract rejects a reordered bench live-check handoff" {
    const reordered =
        \\      - name: Check current Phase 2 closure packet
        \\        run: python3 scripts/zigux/validate-phase2-closure.py
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 1 route summary checker
        \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
        \\      - name: Check current Phase 1 route summary packet
        \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
        \\      - name: Self-test current Phase 1 bench live-check workflow guard
        \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test
        \\      - name: Check current Phase 1 bench live-check workflow guard packet
        \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py
        \\      - name: Self-test current Phase 1 shared reminder checker
        \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
        \\      - name: Check current Phase 1 shared reminder packet
        \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
        \\      - name: Self-test current Phase 1 closure validator
        \\        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
        \\      - name: Check current Phase 1 closure packet
        \\        run: python3 scripts/zigux/validate-phase1-closure.py
        \\      - name: Self-test current Phase 3 interop packet
        \\        run: python3 scripts/zigux/validate_phase3_selftest.py
    ;
    try std.testing.expectError(error.OutOfOrder, validateWorkflow(reordered));
}
