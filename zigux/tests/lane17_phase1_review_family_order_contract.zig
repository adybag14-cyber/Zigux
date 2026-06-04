const std = @import("std");
const options = @import("lane17_phase1_review_family_order_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const workflow = options.workflow_text;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase1_review_family = [_]Gate{
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
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleMarker;
}

fn validateReviewFamilyOrder(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    try requireAfter(&previous, text, "      - name: Self-test current Phase 1 direct-owner checker");
    try requireAfter(&previous, text, "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test");
    try requireAfter(&previous, text, "      - name: Check current Phase 1 direct-owner markers");
    try requireAfter(&previous, text, "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py");

    for (phase1_review_family) |gate| {
        var name_buf: [160]u8 = undefined;
        var command_buf: [192]u8 = undefined;
        const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
        const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
        try requireAfter(&previous, text, name_line);
        try requireAfter(&previous, text, command_line);
    }

    try requireAbsent(text, "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --allow-missing");
    try requireAbsent(text, "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --allow-missing");
    try requireAbsent(text, "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --allow-missing");
    try requireAbsent(text, "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --root");
}

test "current bootstrap workflow keeps the phase1 review-family gates ordered" {
    try validateReviewFamilyOrder(workflow);
}

test "contract rejects missing review-family gate" {
    const fixture =
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Self-test current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test
        \\      - name: Check current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py
    ;

    try std.testing.expectError(error.MissingMarker, validateReviewFamilyOrder(fixture));
}

test "contract rejects reordered helper review commands" {
    const fixture =
        \\      - name: Self-test current Phase 1 direct-owner checker
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\      - name: Check current Phase 1 direct-owner markers
        \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
        \\      - name: Check current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py
        \\      - name: Self-test current Phase 1 direct-anchor manifest gate
        \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test
    ;

    try std.testing.expectError(error.ReorderedMarker, validateReviewFamilyOrder(fixture));
}

test "contract rejects duplicate exact workflow commands" {
    const duplicate = workflow ++ "\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n";

    try std.testing.expectError(error.DuplicateMarker, validateReviewFamilyOrder(duplicate));
}

test "contract rejects stale optional review-family workflow variants" {
    const stale = workflow ++ "\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py --allow-missing\n";

    try std.testing.expectError(error.StaleMarker, validateReviewFamilyOrder(stale));
}
