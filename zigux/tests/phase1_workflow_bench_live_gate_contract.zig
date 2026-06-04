const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "Phase 1 bench live-check workflow guard keeps self-test and live commands paired" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "Self-test current Phase 1 bench checker");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-bench.py --self-test");
    try requireContains(workflow, "Check current Phase 1 bench packet");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-bench.py");

    try requireContains(workflow, "Self-test current Phase 1 bench live-check workflow guard");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test");
    try requireContains(workflow, "Check current Phase 1 bench live-check workflow guard packet");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py");

    try requireContains(workflow, "Self-test current Phase 1 find-bit bench anchor checker");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test");
    try requireContains(workflow, "Check current Phase 1 find-bit bench anchor packet");
    try requireContains(workflow, "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py");
}

test "Phase 1 bench live-check workflow guard stays between bench packet and find-bit anchors" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireBefore(
        workflow,
        "Check current Phase 1 route summary packet",
        "Self-test current Phase 1 bench checker",
    );
    try requireBefore(
        workflow,
        "Self-test current Phase 1 bench checker",
        "Check current Phase 1 bench packet",
    );
    try requireBefore(
        workflow,
        "Check current Phase 1 bench packet",
        "Self-test current Phase 1 bench live-check workflow guard",
    );
    try requireBefore(
        workflow,
        "Self-test current Phase 1 bench live-check workflow guard",
        "Check current Phase 1 bench live-check workflow guard packet",
    );
    try requireBefore(
        workflow,
        "Check current Phase 1 bench live-check workflow guard packet",
        "Self-test current Phase 1 find-bit bench anchor checker",
    );
    try requireBefore(
        workflow,
        "Self-test current Phase 1 find-bit bench anchor checker",
        "Check current Phase 1 find-bit bench anchor packet",
    );
}

test "Phase 1 bench live-check workflow guard remains before shared reminder and closure gates" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireBefore(
        workflow,
        "Check current Phase 1 bench live-check workflow guard packet",
        "Self-test current Phase 1 shared reminder checker",
    );
    try requireBefore(
        workflow,
        "Check current Phase 1 find-bit bench anchor packet",
        "Self-test current Phase 1 shared reminder checker",
    );
    try requireBefore(
        workflow,
        "Check current Phase 1 shared reminder packet",
        "Self-test current Phase 1 closure validator",
    );
    try requireBefore(
        workflow,
        "Self-test current Phase 1 closure validator",
        "Check current Phase 1 closure packet",
    );

    try requireAbsent(workflow, "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --allow-missing");
}
