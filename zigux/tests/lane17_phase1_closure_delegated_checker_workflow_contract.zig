const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const delegated_checker_ladder = [_]Step{
    .{
        .name = "Self-test current Phase 1 direct-owner checker",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-owner markers",
        .run = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .run = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .run = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .run = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .run = "python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .run = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .run = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .run = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .run = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .run = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .run = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
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
};

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireLineOnce(text: []const u8, needle: []const u8) !usize {
    var index: ?usize = null;
    var line_start: usize = 0;
    var count: usize = 0;

    while (line_start <= text.len) {
        const line_end = std.mem.indexOfPos(u8, text, line_start, "\n") orelse text.len;
        const line = std.mem.trim(u8, text[line_start..line_end], " \t\r");
        if (std.mem.eql(u8, line, needle)) {
            count += 1;
            if (index == null) index = line_start;
        }
        if (line_end == text.len) break;
        line_start = line_end + 1;
    }

    try std.testing.expectEqual(@as(usize, 1), count);
    return index.?;
}

fn requireOrderedPair(text: []const u8, step: Step, after: *usize) !void {
    const name_line = try std.fmt.allocPrint(std.testing.allocator, "- name: {s}", .{step.name});
    defer std.testing.allocator.free(name_line);
    const run_line = try std.fmt.allocPrint(std.testing.allocator, "run: {s}", .{step.run});
    defer std.testing.allocator.free(run_line);

    const name_index = try requireLineOnce(text, name_line);
    const run_index = try requireLineOnce(text, run_line);

    try std.testing.expect(name_index > after.*);
    try std.testing.expect(run_index > name_index);
    after.* = run_index;
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(?usize, null), std.mem.indexOf(u8, text, needle));
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn makeWorkflowFixture(allocator: std.mem.Allocator, omit_run: ?[]const u8, duplicate_run: ?[]const u8, swap_tail: bool) ![]u8 {
    var text = std.ArrayList(u8).empty;
    defer text.deinit(allocator);

    try text.appendSlice(allocator, "jobs:\n  bootstrap:\n    steps:\n");
    try text.appendSlice(allocator, "      - name: Check current Phase 2 closure packet\n        run: python3 scripts/zigux/validate-phase2-closure.py\n");

    const cutoff = delegated_checker_ladder.len - 2;
    for (delegated_checker_ladder[0..cutoff]) |step| {
        try appendStep(&text, allocator, step, omit_run, duplicate_run);
    }
    if (swap_tail) {
        try appendStep(&text, allocator, delegated_checker_ladder[cutoff + 1], omit_run, duplicate_run);
        try appendStep(&text, allocator, delegated_checker_ladder[cutoff], omit_run, duplicate_run);
    } else {
        try appendStep(&text, allocator, delegated_checker_ladder[cutoff], omit_run, duplicate_run);
        try appendStep(&text, allocator, delegated_checker_ladder[cutoff + 1], omit_run, duplicate_run);
    }

    try text.appendSlice(allocator, "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n");
    try text.appendSlice(allocator, "      - name: Check current Phase 3 interop packet\n        run: python3 scripts/zigux/run-phase3-checks.py\n");
    return try text.toOwnedSlice(allocator);
}

fn appendStep(
    text: *std.ArrayList(u8),
    allocator: std.mem.Allocator,
    step: Step,
    omit_run: ?[]const u8,
    duplicate_run: ?[]const u8,
) !void {
    const name_line = try std.fmt.allocPrint(allocator, "      - name: {s}\n", .{step.name});
    defer allocator.free(name_line);
    try text.appendSlice(allocator, name_line);
    if (omit_run == null or !std.mem.eql(u8, omit_run.?, step.run)) {
        const run_line = try std.fmt.allocPrint(allocator, "        run: {s}\n", .{step.run});
        defer allocator.free(run_line);
        try text.appendSlice(allocator, run_line);
    }
    if (duplicate_run != null and std.mem.eql(u8, duplicate_run.?, step.run)) {
        const run_line = try std.fmt.allocPrint(allocator, "        run: {s}\n", .{step.run});
        defer allocator.free(run_line);
        try text.appendSlice(allocator, run_line);
    }
}

fn assertWorkflow(text: []const u8) !void {
    try requireContains(text, "run: python3 scripts/zigux/validate-phase2-closure.py");

    var after = try requireLineOnce(text, "run: python3 scripts/zigux/validate-phase2-closure.py");
    for (delegated_checker_ladder) |step| {
        try requireOrderedPair(text, step, &after);
    }

    const phase3_selftest = try requireLineOnce(text, "run: python3 scripts/zigux/validate_phase3_selftest.py");
    const phase3_check = try requireLineOnce(text, "run: python3 scripts/zigux/run-phase3-checks.py");
    try std.testing.expect(phase3_selftest > after);
    try std.testing.expect(phase3_check > phase3_selftest);

    try requireAbsent(text, "make -C zigux phase1-validate");
    try requireAbsent(text, "make -C zigux phase1-test");
    try requireAbsent(text, "make -C zigux phase1-bench");
}

test "live workflow keeps Phase 1 delegated closure checks ordered before Phase 3 handoff" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try assertWorkflow(workflow);
}

test "contract accepts the minimal current delegated-checker ladder fixture" {
    const fixture = try makeWorkflowFixture(std.testing.allocator, null, null, false);
    defer std.testing.allocator.free(fixture);

    try assertWorkflow(fixture);
}

test "contract rejects missing duplicate and swapped delegated-checker workflow drift" {
    const missing = try makeWorkflowFixture(std.testing.allocator, delegated_checker_ladder[2].run, null, false);
    defer std.testing.allocator.free(missing);
    try std.testing.expectError(error.TestExpectedEqual, assertWorkflow(missing));

    const duplicate = try makeWorkflowFixture(std.testing.allocator, null, delegated_checker_ladder[4].run, false);
    defer std.testing.allocator.free(duplicate);
    try std.testing.expectError(error.TestExpectedEqual, assertWorkflow(duplicate));

    const swapped = try makeWorkflowFixture(std.testing.allocator, null, null, true);
    defer std.testing.allocator.free(swapped);
    try std.testing.expectError(error.TestUnexpectedResult, assertWorkflow(swapped));
}
