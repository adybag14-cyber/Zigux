const std = @import("std");
const options = @import("lane17_phase10_phase11_options");

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        options.workflow_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, marker) orelse {
            std.debug.print("missing ordered workflow marker: {s}\n", .{marker});
            return error.MissingWorkflowMarker;
        };
        cursor = found + marker.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    return count;
}

test "phase 10 bootstrap and helper-test block stays internally ordered" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Self-test current Phase 10 bootstrap route checker",
        "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
        "Check current Phase 10 bootstrap route",
        "python3 scripts/zigux/check-phase10-bootstrap-route.py",
        "Validate Phase 10 checker-backed review packet",
        "make -C zigux phase10-validate",
        "Run Phase 10 helper tests",
        "make -C zigux phase10-test",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "make -C zigux phase10-validate"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "make -C zigux phase10-test"));
}

test "phase 11 inventory and support-bundle block stays internally ordered" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Self-test current Phase 11 build inventory checker",
        "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
        "Check current Phase 11 build inventory packet",
        "python3 scripts/zigux/check-phase11-build-inventory.py",
        "Validate current Phase 11 support bundle",
        "make -C zigux phase11-validate",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "python3 scripts/zigux/check-phase11-build-inventory.py --self-test"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "make -C zigux phase11-validate"));
}

test "phase 7 guardrails feed phase 10 before phase 11 begins" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Check current Phase 7 shared-control gap packet",
        "python3 scripts/zigux/check-phase7-shared-control-gap.py",
        "Check current Phase 7 make-wrapper selftest alignment packet",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "Self-test current Phase 10 bootstrap route checker",
        "Run Phase 10 helper tests",
        "Self-test current Phase 11 build inventory checker",
    });
}

test "phase 11 support validation remains before phase 12 expansion gates" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Validate current Phase 11 support bundle",
        "make -C zigux phase11-validate",
        "Self-test current Phase 12 build-only surface checker",
        "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "Check current Phase 12 build inventory packet",
        "python3 scripts/zigux/check-phase12-build-inventory.py",
    });
}

test "workflow triggers still include Zigux and workflow edits for this guard" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "pull_request:");
    try expectContains(workflow, "- 'zigux/**'");
    try expectContains(workflow, "- '.github/workflows/zigux-bootstrap.yml'");
    try expectContains(workflow, "workflow_dispatch:");
}
