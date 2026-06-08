const std = @import("std");

const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleAggregateRoute,
};

const Marker = struct {
    name: []const u8,
    line: []const u8,
};

const phase1_direct_review_ladder = [_]Marker{
    .{ .name = "phase2 aggregate handoff", .line = "        run: make -C zigux phase2" },
    .{ .name = "direct owner self-test", .line = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test" },
    .{ .name = "direct owner packet", .line = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py" },
    .{ .name = "direct anchor manifest self-test", .line = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test" },
    .{ .name = "direct anchor manifest packet", .line = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py" },
    .{ .name = "string review self-test", .line = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test" },
    .{ .name = "string review packet", .line = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py" },
    .{ .name = "find-bit review self-test", .line = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test" },
    .{ .name = "find-bit review packet", .line = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py" },
    .{ .name = "bitmap direct anchor self-test", .line = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test" },
    .{ .name = "bitmap direct anchor packet", .line = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py" },
    .{ .name = "rbtree review self-test", .line = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test" },
    .{ .name = "rbtree review packet", .line = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py" },
    .{ .name = "route summary self-test", .line = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test" },
    .{ .name = "route summary packet", .line = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py" },
    .{ .name = "bench self-test", .line = "        run: python3 scripts/zigux/check-phase1-bench.py --self-test" },
    .{ .name = "bench packet", .line = "        run: python3 scripts/zigux/check-phase1-bench.py" },
    .{ .name = "bench live-check workflow self-test", .line = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test" },
    .{ .name = "bench live-check workflow packet", .line = "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py" },
    .{ .name = "find-bit bench anchor self-test", .line = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test" },
    .{ .name = "find-bit bench anchor packet", .line = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py" },
    .{ .name = "shared reminder self-test", .line = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test" },
    .{ .name = "shared reminder packet", .line = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py" },
    .{ .name = "closure validator self-test", .line = "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test" },
    .{ .name = "closure packet", .line = "        run: python3 scripts/zigux/validate-phase1-closure.py" },
    .{ .name = "phase3 interop self-test", .line = "        run: python3 scripts/zigux/validate_phase3_selftest.py" },
};

fn readWorkflowSource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    var env_map = try std.testing.environ.createMap(std.testing.allocator);
    defer env_map.deinit();
    const path = env_map.get("LANE17_WORKFLOW_PATH") orelse default_workflow_path;

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn countLineOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trimEnd(u8, line, "\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn findLineIndex(source: []const u8, needle: []const u8) ?usize {
    var line_index: usize = 0;
    var lines = std.mem.splitScalar(u8, source, '\n');
    while (lines.next()) |line| : (line_index += 1) {
        if (std.mem.eql(u8, std.mem.trimEnd(u8, line, "\r"), needle)) {
            return line_index;
        }
    }
    return null;
}

fn requireOnceAfter(source: []const u8, needle: []const u8, previous_line_index: usize) !usize {
    const occurrences = countLineOccurrences(source, needle);
    if (occurrences == 0) return ContractError.MissingMarker;
    if (occurrences != 1) return ContractError.DuplicateMarker;
    const line_index = findLineIndex(source, needle).?;
    if (line_index <= previous_line_index) return ContractError.ReorderedMarker;
    return line_index;
}

fn verifyPhase1DirectReviewWorkflow(source: []const u8) !void {
    if (std.mem.indexOf(u8, source, "        run: make -C zigux phase1\n") != null) {
        return ContractError.StaleAggregateRoute;
    }
    if (std.mem.indexOf(u8, source, "        run: zig build phase1") != null) {
        return ContractError.StaleAggregateRoute;
    }

    var previous_index: usize = 0;
    for (phase1_direct_review_ladder) |marker| {
        previous_index = try requireOnceAfter(source, marker.line, previous_index);
    }
}

fn compactWorkflow(markers: []const Marker) []const u8 {
    _ = markers;
    return
    \\name: zigux-bootstrap
    \\jobs:
    \\  bootstrap:
    \\    steps:
    \\      - name: Run current Phase 2 aggregate make route
    \\        run: make -C zigux phase2
    \\      - name: Self-test current Phase 1 direct-owner checker
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    \\      - name: Check current Phase 1 direct-owner markers
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
    \\      - name: Self-test current Phase 1 direct-anchor manifest gate
    \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test
    \\      - name: Check current Phase 1 direct-anchor manifest gate
    \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py
    \\      - name: Self-test current Phase 1 string review checker
    \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test
    \\      - name: Check current Phase 1 string review packet
    \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py
    \\      - name: Self-test current Phase 1 find-bit review checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test
    \\      - name: Check current Phase 1 find-bit review packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py
    \\      - name: Self-test current Phase 1 bitmap direct-anchor checker
    \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test
    \\      - name: Check current Phase 1 bitmap direct-anchor packet
    \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py
    \\      - name: Self-test current Phase 1 rbtree review checker
    \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test
    \\      - name: Check current Phase 1 rbtree review packet
    \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py
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
    \\
    ;
}

test "live workflow preserves the phase1 direct-review checker ladder" {
    const source = try readWorkflowSource();
    defer std.testing.allocator.free(source);

    try verifyPhase1DirectReviewWorkflow(source);
}

test "contract accepts the compact current marker ladder" {
    try verifyPhase1DirectReviewWorkflow(compactWorkflow(&phase1_direct_review_ladder));
}

test "contract rejects missing or duplicated focused markers" {
    const missing_find_bit =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Run current Phase 2 aggregate make route
        \\        run: make -C zigux phase2
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\
    ;
    try std.testing.expectError(ContractError.MissingMarker, verifyPhase1DirectReviewWorkflow(missing_find_bit));

    const duplicated =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Run current Phase 2 aggregate make route
        \\        run: make -C zigux phase2
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test
        \\      - name: Check current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py
        \\      - name: Self-test current Phase 1 string review checker
        \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test
        \\      - name: Check current Phase 1 string review packet
        \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py
        \\      - name: Self-test current Phase 1 find-bit review checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test
        \\      - name: Check current Phase 1 find-bit review packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py
        \\      - name: Self-test current Phase 1 bitmap direct-anchor checker
        \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test
        \\      - name: Check current Phase 1 bitmap direct-anchor packet
        \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py
        \\      - name: Self-test current Phase 1 rbtree review checker
        \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test
        \\      - name: Check current Phase 1 rbtree review packet
        \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py
        \\      - name: Self-test current Phase 1 route summary checker
        \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
        \\      - name: Check current Phase 1 route summary packet
        \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\      - name: Duplicate Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\      - name: Self-test current Phase 1 bench live-check workflow guard
        \\        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test
        \\
    ;
    try std.testing.expectError(ContractError.DuplicateMarker, verifyPhase1DirectReviewWorkflow(duplicated));
}

test "contract rejects reordered handoffs and stale aggregate routes" {
    const reordered =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Run current Phase 2 aggregate make route
        \\        run: make -C zigux phase2
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\
    ;
    try std.testing.expectError(ContractError.ReorderedMarker, verifyPhase1DirectReviewWorkflow(reordered));

    const stale_aggregate =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Run current Phase 2 aggregate make route
        \\        run: make -C zigux phase2
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Stale aggregate Phase 1 route
        \\        run: make -C zigux phase1
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\
    ;
    try std.testing.expectError(ContractError.StaleAggregateRoute, verifyPhase1DirectReviewWorkflow(stale_aggregate));
}
