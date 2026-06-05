const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_route_summary_selftest = Command{
    .name = "Self-test current Phase 1 route summary checker",
    .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
};

const phase1_route_summary_check = Command{
    .name = "Check current Phase 1 route summary packet",
    .run = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn requireCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    try std.testing.expectEqual(expected_count, countOccurrences(haystack, needle));
}

fn markerFor(command: Command, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "- name: {s}\n        run: {s}\n",
        .{ command.name, command.run },
    );
}

fn commandLineFor(command: Command, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "        run: {s}\n",
        .{command.run},
    );
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, marker).?);
    return index;
}

fn commandIndex(command: Command, allocator: std.mem.Allocator) !usize {
    const marker = try markerFor(command, allocator);
    defer allocator.free(marker);
    return markerIndex(workflow_text, marker);
}

test "workflow keeps route-summary self-test and packet check as exact run lines" {
    const selftest_marker = try markerFor(phase1_route_summary_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_route_summary_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);
    const selftest_run = try commandLineFor(phase1_route_summary_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_run);
    const check_run = try commandLineFor(phase1_route_summary_check, std.testing.allocator);
    defer std.testing.allocator.free(check_run);

    try requireContains(workflow_text, selftest_marker);
    try requireContains(workflow_text, check_marker);
    try requireCount(workflow_text, selftest_marker, 1);
    try requireCount(workflow_text, check_marker, 1);
    try requireCount(workflow_text, selftest_run, 1);
    try requireCount(workflow_text, check_run, 1);
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --root",
    );
    try requireMissing(
        workflow_text,
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --allow-missing",
    );
}

test "route-summary live check follows its self-test before bench gates" {
    const selftest_index = try commandIndex(phase1_route_summary_selftest, std.testing.allocator);
    const check_index = try commandIndex(phase1_route_summary_check, std.testing.allocator);
    const bench_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
    );
    const bench_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
    );
    const live_check_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 bench live-check workflow guard\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test\n",
    );
    const find_bit_bench_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 find-bit bench anchor checker\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n",
    );

    try std.testing.expect(selftest_index < check_index);
    try std.testing.expect(check_index < bench_selftest_index);
    try std.testing.expect(bench_selftest_index < bench_check_index);
    try std.testing.expect(bench_check_index < live_check_index);
    try std.testing.expect(live_check_index < find_bit_bench_index);
}

test "route-summary gate stays after helper review gates and before closure/smoke" {
    const direct_owner_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 direct-owner markers\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
    );
    const direct_anchor_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 direct-anchor manifest gate\n        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
    );
    const string_review_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 string review packet\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n",
    );
    const find_bit_review_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 find-bit review packet\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n",
    );
    const bitmap_direct_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 bitmap direct-anchor packet\n        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py\n",
    );
    const rbtree_review_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 rbtree review packet\n        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py\n",
    );
    const route_summary_index = try commandIndex(phase1_route_summary_check, std.testing.allocator);
    const shared_reminder_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 shared reminder checker\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    );
    const closure_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    );
    const smoke_index = try markerIndex(
        workflow_text,
        "- name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try std.testing.expect(direct_owner_index < direct_anchor_index);
    try std.testing.expect(direct_anchor_index < string_review_index);
    try std.testing.expect(string_review_index < find_bit_review_index);
    try std.testing.expect(find_bit_review_index < bitmap_direct_index);
    try std.testing.expect(bitmap_direct_index < rbtree_review_index);
    try std.testing.expect(rbtree_review_index < route_summary_index);
    try std.testing.expect(route_summary_index < shared_reminder_index);
    try std.testing.expect(shared_reminder_index < closure_index);
    try std.testing.expect(closure_index < smoke_index);
}

test "phase1 workflow contract keeps each checked command singular" {
    const checked_markers = [_][]const u8{
        "- name: Check current Phase 1 direct-owner markers\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
        "- name: Check current Phase 1 direct-anchor manifest gate\n        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
        "- name: Check current Phase 1 string review packet\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n",
        "- name: Check current Phase 1 find-bit review packet\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n",
        "- name: Check current Phase 1 bitmap direct-anchor packet\n        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py\n",
        "- name: Check current Phase 1 rbtree review packet\n        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py\n",
        "- name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
        "- name: Check current Phase 1 bench live-check workflow guard packet\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py\n",
        "- name: Check current Phase 1 find-bit bench anchor packet\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n",
        "- name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
        "- name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n",
    };

    for (checked_markers) |marker| {
        try requireCount(workflow_text, marker, 1);
    }
}
