const std = @import("std");
const perf_buffer_poll = @import("perf_buffer_poll");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "perf_buffer__poll(timeout_ms)");
    try expectContains(note, "wait-result classification");
    try expectContains(note, "normalized negative errno-or-ready-count wait results");
    try expectContains(note, "ready-buffer bookkeeping");
    try expectContains(note, "no standalone timer helper");
    try expectContains(note, "no standalone clockevent helper");
}

test "phase 8 perf-buffer poll helper stays wired into the shared Phase 8 build" {
    const build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(build_file, "phase8_perf_buffer_poll.zig");
    try expectContains(build_file, "phase8-perf-buffer-poll-tests");
}

test "phase 8 perf-buffer poll helper keeps observed wait outcomes compact" {
    const buffers = [_]perf_buffer_poll.BufferObservation{
        .{ .ready = true },
        .{},
        .{ .error_code = -5 },
    };

    const summary = try perf_buffer_poll.summarizePoll(12, .{ .ready_events = 2 }, &buffers);
    try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, summary.wait_class);
    try std.testing.expectEqual(perf_buffer_poll.PollOutcome.ready, summary.outcome);
    try std.testing.expectEqual(@as(usize, 1), summary.ready_count);
    try std.testing.expectEqual(@as(?i32, -5), summary.first_error);
}

test "phase 8 perf-buffer poll helper normalizes observed wait results before summarizing buffers" {
    const ready = perf_buffer_poll.classifyObservedWaitResult(2);
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .ready_events = 2 },
        ready,
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation.interrupted,
        perf_buffer_poll.classifyObservedWaitResult(-@as(i32, @intFromEnum(std.os.linux.E.INTR))),
    );
    try std.testing.expectEqualDeep(
        perf_buffer_poll.WaitObservation{ .failed = -5 },
        perf_buffer_poll.classifyObservedWaitResult(-5),
    );
}
