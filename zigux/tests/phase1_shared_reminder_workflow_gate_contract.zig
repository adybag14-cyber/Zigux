const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Command = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_shared_reminder_selftest = Command{
    .name = "Self-test current Phase 1 shared reminder checker",
    .run = "zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test",
};

const phase1_shared_reminder_check = Command{
    .name = "Check current Phase 1 shared reminder packet",
    .run = "zig run scripts/zigux/check_phase1_shared_reminder_packet.zig",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn markerFor(command: Command, allocator: std.mem.Allocator) ![]u8 {
    return try std.fmt.allocPrint(
        allocator,
        "- name: {s}\n        run: {s}\n",
        .{ command.name, command.run },
    );
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, marker).?);
    return index;
}

test "workflow keeps shared reminder self-test and packet check as exact run lines" {
    const selftest_marker = try markerFor(phase1_shared_reminder_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_shared_reminder_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    try requireContains(workflow_text, selftest_marker);
    try requireContains(workflow_text, check_marker);
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --root",
    );
    try requireMissing(
        workflow_text,
        "run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --allow-missing",
    );
}

test "shared reminder live check follows its self-test after bench gates" {
    const selftest_marker = try markerFor(phase1_shared_reminder_selftest, std.testing.allocator);
    defer std.testing.allocator.free(selftest_marker);
    const check_marker = try markerFor(phase1_shared_reminder_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const bench_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 bench checker\n        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test\n",
    );
    const find_bit_bench_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 find-bit bench anchor packet\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig\n",
    );
    const selftest_index = try markerIndex(workflow_text, selftest_marker);
    const check_index = try markerIndex(workflow_text, check_marker);

    try std.testing.expect(bench_selftest_index < find_bit_bench_check_index);
    try std.testing.expect(find_bit_bench_check_index < selftest_index);
    try std.testing.expect(selftest_index < check_index);
}

test "shared reminder gate stays before closure and final Phase 1 smoke" {
    const check_marker = try markerFor(phase1_shared_reminder_check, std.testing.allocator);
    defer std.testing.allocator.free(check_marker);

    const shared_reminder_index = try markerIndex(workflow_text, check_marker);
    const closure_selftest_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 1 closure validator\n        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test\n",
    );
    const closure_check_index = try markerIndex(
        workflow_text,
        "- name: Check current Phase 1 closure packet\n        run: zig run scripts/zigux/validate_phase1_closure.zig\n",
    );
    const phase3_interop_index = try markerIndex(
        workflow_text,
        "- name: Self-test current Phase 3 interop packet\n        run: zig run scripts/zigux/validate_phase3_selftest.zig\n",
    );
    const smoke_index = try markerIndex(
        workflow_text,
        "- name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try std.testing.expect(shared_reminder_index < closure_selftest_index);
    try std.testing.expect(closure_selftest_index < closure_check_index);
    try std.testing.expect(closure_check_index < phase3_interop_index);
    try std.testing.expect(phase3_interop_index < smoke_index);
}
