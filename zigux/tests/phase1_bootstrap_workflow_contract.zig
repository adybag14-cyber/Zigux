const std = @import("std");

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(workflow: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, workflow, needle) != null);
}

fn requireOrdered(workflow: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, workflow, before) orelse return error.MissingBeforeMarker;
    const after_tail = workflow[before_index + before.len ..];
    _ = std.mem.indexOf(u8, after_tail, after) orelse return error.MissingAfterMarker;
}

test "bootstrap workflow watches Phase 1 lane-owned path surfaces" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "- 'scripts/zigux/**'");
    try requireContains(workflow, "- 'tools/lib/*.zig'");
    try requireContains(workflow, "- 'zigux/**'");
    try requireContains(workflow, "- '.github/workflows/zigux-bootstrap.yml'");
}

test "bootstrap workflow keeps paired Phase 1 checker gates fail closed" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const paired_gates = [_]struct { self_test: []const u8, packet: []const u8 }{
        .{
            .self_test = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-string-review-packet.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        },
        .{
            .self_test = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
            .packet = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        },
        .{
            .self_test = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
            .packet = "python3 scripts/zigux/validate-phase1-closure.py",
        },
    };

    for (paired_gates) |gate| {
        try requireOrdered(workflow, gate.self_test, gate.packet);
    }
}

test "bootstrap workflow keeps Phase 1 bench and shared smoke routes visible" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "python3 scripts/zigux/check-phase1-bench.py --self-test");
    try requireOrdered(
        workflow,
        "python3 scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    );
    try requireContains(workflow, "Run current Phase 1 shared tests-root smoke");
}
