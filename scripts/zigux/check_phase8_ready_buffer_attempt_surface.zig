const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_READY_BUFFER_ATTEMPT_SURFACE=pass";
pub const self_test_pass_marker = "PHASE8_READY_BUFFER_ATTEMPT_SURFACE_SELF_TEST=pass";

const HELPER_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
};

const HELPER_MARKERS = [_][]const u8{
    "pub const ReadyBufferAttemptLookupDisposition = enum {",
    "pub const ReadyBufferAttemptLookupSummary = struct {",
    "requested_attempt_index: usize,",
    "ready_index: ?usize,",
    "ready_count: usize,",
    "pub const ReadyBufferAttemptLookupError = error{",
    "pub fn resolveReadyBufferAttemptIndex(",
    "pub fn summarizeReadyBufferAttemptLookup(",
    "pub fn resolveReadyBufferAttemptLookup(",
    "test \"phase8 perf-buffer poll resolves ready-buffer attempt ordinals back to slot indexes\" {",
    "test \"phase8 perf-buffer poll exposes typed ready-buffer attempt lookup summaries\" {",
    "try std.testing.expectEqual(@as(?usize, 1), resolveReadyBufferAttemptIndex(&buffers, 0));",
    "try std.testing.expectEqual(@as(usize, 2), first.ready_count);",
    "try std.testing.expectError(error.MissingReadyBuffer, resolveReadyBufferAttemptLookup(missing));",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_helper_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    defer allocator.free(text_helper_path_path);
    const text_helper_path = try guard.readUtf8File(io, allocator, text_helper_path_path);
    defer allocator.free(text_helper_path);
    for (HELPER_PATH) |marker| try guard.requireMarker(text_helper_path, marker);
    const text_helper_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    defer allocator.free(text_helper_markers_path);
    const text_helper_markers = try guard.readUtf8File(io, allocator, text_helper_markers_path);
    defer allocator.free(text_helper_markers);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text_helper_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
