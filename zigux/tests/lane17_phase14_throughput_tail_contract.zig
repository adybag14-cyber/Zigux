const std = @import("std");
const options = @import("lane17_phase14_tail_options");

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

fn indexOfLastNonWhitespaceByte(text: []const u8) ?usize {
    if (text.len == 0) return null;

    var index = text.len;
    while (index > 0) {
        index -= 1;
        switch (text[index]) {
            ' ', '\n', '\r', '\t' => {},
            else => return index,
        }
    }
    return null;
}

fn expectTerminalMarker(haystack: []const u8, marker: []const u8) !void {
    const marker_index = std.mem.lastIndexOf(u8, haystack, marker) orelse {
        std.debug.print("missing terminal workflow marker: {s}\n", .{marker});
        return error.MissingWorkflowMarker;
    };
    const marker_end = marker_index + marker.len;
    const final_non_ws = indexOfLastNonWhitespaceByte(haystack) orelse return error.EmptyWorkflow;
    try std.testing.expectEqual(marker_end - 1, final_non_ws);
}

test "phase 14 shared smoke checker still gates the validate route" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Self-test current Phase 14 shared smoke route checker",
        "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
        "Run current Phase 14 validate route",
        "make -C zigux phase14-validate",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "make -C zigux phase14-validate"));
}

test "phase 12 throughput parity remains after phase 14 validate" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "Run current Phase 14 validate route",
        "make -C zigux phase14-validate",
        "Run current Phase 12 throughput-parity anchor",
        "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    });
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all"));
}

test "throughput parity anchor remains the terminal workflow command" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectTerminalMarker(
        workflow,
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    );
}

test "workflow triggers still cover Zigux tests and workflow edits" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "pull_request:");
    try expectContains(workflow, "- 'zigux/**'");
    try expectContains(workflow, "- '.github/workflows/zigux-bootstrap.yml'");
    try expectContains(workflow, "workflow_dispatch:");
}
