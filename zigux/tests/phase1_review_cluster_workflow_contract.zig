const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Step = struct {
    name: []const u8,
    command: []const u8,
};

const review_steps = [_]Step{
    .{
        .name = "Self-test current Phase 1 direct-anchor manifest gate",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "Check current Phase 1 direct-anchor manifest gate",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "Self-test current Phase 1 string review checker",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 string review packet",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 find-bit review checker",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 find-bit review packet",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 bitmap direct-anchor checker",
        .command = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "Check current Phase 1 bitmap direct-anchor packet",
        .command = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "Self-test current Phase 1 rbtree review checker",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 1 rbtree review packet",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "Self-test current Phase 1 route summary checker",
        .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "Check current Phase 1 route summary packet",
        .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
};

const stale_variants = [_][]const u8{
    "python3 scripts/zigux/check-phase1-string-review-packet.py --root",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --allow-missing",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --root",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --allow-missing",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --root",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --allow-missing",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --root",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --allow-missing",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --root",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --allow-missing",
};

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !usize {
    const count = countOccurrences(haystack, needle);
    try std.testing.expectEqual(@as(usize, 1), count);
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn stepNameMarker(name: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "- name: {s}", .{name});
}

fn runMarker(command: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "\n        run: {s}\n", .{command});
}

test "Phase 1 review workflow keeps exact checker commands" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    for (review_steps) |step| {
        var name_buffer: [160]u8 = undefined;
        var run_buffer: [180]u8 = undefined;
        _ = try expectOnce(workflow, try stepNameMarker(step.name, &name_buffer));
        _ = try expectOnce(workflow, try runMarker(step.command, &run_buffer));
    }

    for (stale_variants) |variant| {
        try expectAbsent(workflow, variant);
    }
}

test "Phase 1 review workflow keeps the helper review cluster ordered" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    var previous_index: usize = 0;
    for (review_steps, 0..) |step, index| {
        var name_buffer: [160]u8 = undefined;
        const current_index = try expectOnce(workflow, try stepNameMarker(step.name, &name_buffer));
        if (index > 0) {
            try std.testing.expect(previous_index < current_index);
        }
        previous_index = current_index;
    }
}

test "Phase 1 review workflow stays between direct gates and downstream bench gates" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const direct_owner = try expectOnce(
        workflow,
        "- name: Check current Phase 1 direct-owner markers",
    );
    const direct_anchor = try expectOnce(
        workflow,
        "- name: Check current Phase 1 direct-anchor manifest gate",
    );
    const string_review = try expectOnce(
        workflow,
        "- name: Self-test current Phase 1 string review checker",
    );
    const route_summary = try expectOnce(
        workflow,
        "- name: Check current Phase 1 route summary packet",
    );
    const bench = try expectOnce(
        workflow,
        "- name: Self-test current Phase 1 bench checker",
    );
    const shared_reminder = try expectOnce(
        workflow,
        "- name: Self-test current Phase 1 shared reminder checker",
    );

    try std.testing.expect(direct_owner < direct_anchor);
    try std.testing.expect(direct_anchor < string_review);
    try std.testing.expect(string_review < route_summary);
    try std.testing.expect(route_summary < bench);
    try std.testing.expect(bench < shared_reminder);
}
