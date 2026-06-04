const std = @import("std");

const workflow_path = @import("build_options").workflow_path;

const Step = struct {
    block: []const u8,
};

const required_steps = [_]Step{
    .{
        .block = "      - name: Check current Phase 1 route summary packet\n" ++
            "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .block = "      - name: Self-test current Phase 1 bench checker\n" ++
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .block = "      - name: Check current Phase 1 bench packet\n" ++
            "        run: python3 scripts/zigux/check-phase1-bench.py",
    },
    .{
        .block = "      - name: Self-test current Phase 1 bench live-check workflow guard\n" ++
            "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    },
    .{
        .block = "      - name: Check current Phase 1 bench live-check workflow guard packet\n" ++
            "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    },
    .{
        .block = "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
            "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .block = "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
            "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .block = "      - name: Self-test current Phase 1 shared reminder checker\n" ++
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn requireSingleOffset(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    if (std.mem.indexOfPos(u8, haystack, first + needle.len, needle) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requireStepCluster(workflow: []const u8) !void {
    var previous_offset: ?usize = null;
    for (required_steps) |step| {
        const offset = try requireSingleOffset(workflow, step.block);
        if (previous_offset) |previous| {
            try std.testing.expect(previous < offset);
        }
        previous_offset = offset;
    }
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(512 * 1024),
    );
}

test "live Phase 1 bench workflow cluster is exact and ordered" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireStepCluster(workflow);
}

test "bench live packet is not confused with its self-test command" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try std.testing.expectEqual(
        @as(usize, 1),
        countOccurrences(workflow, "        run: python3 scripts/zigux/check-phase1-bench.py\n"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        countOccurrences(workflow, "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n"),
    );
}

test "bench live-check workflow guard keeps self-test before packet check" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const self_test = try requireSingleOffset(
        workflow,
        "      - name: Self-test current Phase 1 bench live-check workflow guard\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    );
    const packet = try requireSingleOffset(
        workflow,
        "      - name: Check current Phase 1 bench live-check workflow guard packet\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    );
    try std.testing.expect(self_test < packet);
}

test "required cluster rejects missing live bench packet in synthetic workflow" {
    const missing_live_bench =
        "      - name: Check current Phase 1 route summary packet\n" ++
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n\n" ++
        "      - name: Self-test current Phase 1 bench checker\n" ++
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n\n" ++
        "      - name: Self-test current Phase 1 bench live-check workflow guard\n" ++
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test\n\n" ++
        "      - name: Check current Phase 1 bench live-check workflow guard packet\n" ++
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py\n\n" ++
        "      - name: Self-test current Phase 1 find-bit bench anchor checker\n" ++
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n\n" ++
        "      - name: Check current Phase 1 find-bit bench anchor packet\n" ++
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n\n" ++
        "      - name: Self-test current Phase 1 shared reminder checker\n" ++
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test";

    try std.testing.expectError(error.MissingWorkflowMarker, requireStepCluster(missing_live_bench));
}
