const std = @import("std");
const options = @import("lane17_phase11_phase12_options");

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

test "phase 11 build inventory and support bundle stay internally ordered" {
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
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "run: python3 scripts/zigux/check-phase11-build-inventory.py\n"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "make -C zigux phase11-validate"));
}

test "phase 12 build inventory and driver packet checks stay internally ordered" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Self-test current Phase 12 build-only surface checker",
        "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "Check current Phase 12 build-only surface",
        "python3 scripts/zigux/check-build-only-phase12-surface.py",
        "Self-test current Phase 12 build inventory checker",
        "python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
        "Check current Phase 12 build inventory packet",
        "python3 scripts/zigux/check-phase12-build-inventory.py",
        "Self-test current Phase 12 complex-driver lane packet checker",
        "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
        "Check current Phase 12 complex-driver lane packet",
        "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
        "Self-test current Phase 12 cross-compile smoke checker",
        "python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
        "Check current Phase 12 cross-compile smoke packet",
        "python3 scripts/zigux/check-phase12-cross-compile-smoke.py",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "python3 scripts/zigux/check-phase12-build-inventory.py --self-test"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test"));
}

test "phase 12 release and libbpf checks stay before validate and make routes" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Self-test current Phase 12 release-readiness packet checker",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "Check current Phase 12 release-readiness packet",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "Self-test current Phase 12 libbpf snapshot checker",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
        "Check current Phase 12 libbpf snapshot packet",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
        "Self-test current Phase 12 libbpf heavy-consumer packet checker",
        "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
        "Check current Phase 12 libbpf heavy-consumer packet",
        "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "Validate current Phase 12 support bundle",
        "python3 scripts/zigux/validate-phase12.py",
        "Run current Phase 12 smoke packet",
        "make -C zigux phase12-smoke",
        "Run current Phase 12 shared test packet",
        "make -C zigux phase12-test",
        "Run current Phase 12 aggregate route",
        "make -C zigux phase12",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "python3 scripts/zigux/validate-phase12.py"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "run: make -C zigux phase12\n"));
}

test "phase 11 support validation hands off to phase 12 before later phase 14 checks" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Validate current Phase 11 support bundle",
        "make -C zigux phase11-validate",
        "Self-test current Phase 12 build-only surface checker",
        "Validate current Phase 12 support bundle",
        "Run current Phase 12 aggregate route",
        "Self-test current Phase 14 shared smoke route checker",
        "Run current Phase 14 validate route",
        "Run current Phase 12 throughput-parity anchor",
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
