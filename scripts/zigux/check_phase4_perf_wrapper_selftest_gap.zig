const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_WRAPPER_SELFTEST_GAP=pass";
pub const self_test_pass_marker = "PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=pass";

const PERF_THRESHOLD_SELFTEST = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig -- --self-test",
};

const PERF_THRESHOLD_LIVE = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig",
};

const PERF_BASELINE_SELFTEST = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig -- --self-test",
};

const PERF_BASELINE_LIVE = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "CheckSpec(\"phase4-perf-baseline-packet-self-test\", (\"python\", \"scripts\\zigux/check_phase4_perf_baseline_packet.zig\", \"--self-test\"))",
    "CheckSpec(\"phase4-perf-baseline-packet\", (\"python\", \"scripts\\zigux/check_phase4_perf_baseline_packet.zig\"))",
    "CheckSpec(\"phase4-perf-threshold-matrix-self-test\", (\"python\", \"scripts\\zigux/check_phase4_perf_threshold_matrix.zig\", \"--self-test\"))",
    "CheckSpec(\"phase4-perf-threshold-matrix\", (\"python\", \"scripts\\zigux/check_phase4_perf_threshold_matrix.zig\"))",
};

const MATRIX_MARKERS = [_][]const u8{
    "local-only benchmark commands and acceptable limits are approved today",
    "shared CI perf promotion pending",
    "current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_perf_threshold_selftest_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_perf_threshold_selftest_path);
    const text_perf_threshold_selftest = try guard.readUtf8File(io, allocator, text_perf_threshold_selftest_path);
    defer allocator.free(text_perf_threshold_selftest);
    for (PERF_THRESHOLD_SELFTEST) |marker| try guard.requireMarker(text_perf_threshold_selftest, marker);
    const text_perf_threshold_live_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_perf_threshold_live_path);
    const text_perf_threshold_live = try guard.readUtf8File(io, allocator, text_perf_threshold_live_path);
    defer allocator.free(text_perf_threshold_live);
    for (PERF_THRESHOLD_LIVE) |marker| try guard.requireMarker(text_perf_threshold_live, marker);
    const text_perf_baseline_selftest_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_perf_baseline_selftest_path);
    const text_perf_baseline_selftest = try guard.readUtf8File(io, allocator, text_perf_baseline_selftest_path);
    defer allocator.free(text_perf_baseline_selftest);
    for (PERF_BASELINE_SELFTEST) |marker| try guard.requireMarker(text_perf_baseline_selftest, marker);
    const text_perf_baseline_live_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_perf_baseline_live_path);
    const text_perf_baseline_live = try guard.readUtf8File(io, allocator, text_perf_baseline_live_path);
    defer allocator.free(text_perf_baseline_live);
    for (PERF_BASELINE_LIVE) |marker| try guard.requireMarker(text_perf_baseline_live, marker);
    const text_validator_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase4.zig");
    defer allocator.free(text_validator_markers_path);
    const text_validator_markers = try guard.readUtf8File(io, allocator, text_validator_markers_path);
    defer allocator.free(text_validator_markers);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text_validator_markers, marker);
    const text_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_markers_path);
    const text_matrix_markers = try guard.readUtf8File(io, allocator, text_matrix_markers_path);
    defer allocator.free(text_matrix_markers);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text_matrix_markers, marker);
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
