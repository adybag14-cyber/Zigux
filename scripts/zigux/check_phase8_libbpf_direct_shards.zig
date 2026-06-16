const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_LIBBPF_DIRECT_SHARDS_SELFTEST=pass";
pub const self_test_pass_marker = "PHASE8_LIBBPF_DIRECT_SHARDS_SELFTEST_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "tools/lib/bpf/zigux_segments/verify.zig",
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    "tools/lib/bpf/zigux_segments/logging.zig",
    "tools/lib/bpf/zigux_segments/type_names.zig",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/Makefile` Phase 8 route family are current exact-readable evidence",
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the bounded `make -C zigux phase8-perf-buffer-poll-test` route already keep the timing-adjacent no-timer and no-clockevent boundary explicit without claiming broader timeout-sensitive routing behavior",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase8-libbpf-segments-test:",
    "phase8-perf-buffer-poll-test:",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
    const text_makefile_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer allocator.free(text_makefile_markers_path);
    const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
    defer allocator.free(text_makefile_markers);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
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
