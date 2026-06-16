const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE8_TESTS_README_LIBBPF_PACKET=pass";
pub const self_test_pass_marker = "CHECK_PHASE8_TESTS_README_LIBBPF_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    "`zigux/tests/phase8_cpu_mask.zig`",
    "`zigux/tests/phase8_logging.zig`",
    "`zigux/tests/phase8_pin_path.zig`",
    "`zigux/tests/phase8_bpf_type_names.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_libbpf_segments.zig`",
    "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`scripts\\zigux/check_phase8_libbpf_segment_gate.zig`",
    "`scripts\\zigux/check_phase8_libbpf_shard_routes.zig`",
    "`make -C zigux phase8-cpu-mask-test`",
    "`make -C zigux phase8-file-path-handle-bridge-test`",
    "`make -C zigux phase8-libbpf-segments-test`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
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
