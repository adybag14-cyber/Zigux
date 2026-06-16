const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_CONTROL_PLANE_ROUTES=pass";
pub const self_test_pass_marker = "PHASE8_CONTROL_PLANE_ROUTES_SELF_TEST=pass";

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\\zigux/validate_phase8.zig",
};

const PHASE8_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_perf_buffer_poll.zig",
};

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "Validate Phase 8 tooling gates",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 libbpf segment survey tests",
    "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
};

const VALIDATOR_REQUIRED_MARKERS = [_][]const u8{
    "MAKEFILE_PATH = \"zigux/Makefile\"",
    "VALIDATOR_PATH = \"scripts\\zigux/validate_phase8.zig\"",
    "PERF_BUFFER_POLL_GATE_PATH = \"scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig\"",
    "LIBBPF_SEGMENT_GATE_PATH = \"scripts\\zigux/check_phase8_libbpf_segment_gate.zig\"",
    "LIBBPF_SHARD_ROUTES_PATH = \"scripts\\zigux/check_phase8_libbpf_shard_routes.zig\"",
    "LIBBPF_SEGMENT_SURVEY_PATH = \"Documentation/zigux/phase8-libbpf-segment-survey.md\"",
    "BRIDGE_SLICE_PATH = \"Documentation/zigux/phase8-file-path-handle-bridge-slice.md\"",
    "BRIDGE_BUILD_PATH = \"zigux/tests/phase8_file_path_handle_bridge_only_build.zig\"",
    "PHASE8_BUILD_PATH = \"zigux/tests/phase8_build.zig\"",
};

const PHASE8_TEST_REQUIRED_MARKERS = [_][]const u8{
    "\"Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md\"",
    "\"zigux/tests/phase8_perf_buffer_poll_only_build.zig\"",
    "\"zig run scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path_path);
    const text_workflow_path = try guard.readUtf8File(io, allocator, text_workflow_path_path);
    defer allocator.free(text_workflow_path);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text_workflow_path, marker);
    const text_validator_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_path_path);
    const text_validator_path = try guard.readUtf8File(io, allocator, text_validator_path_path);
    defer allocator.free(text_validator_path);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text_validator_path, marker);
    const text_phase8_test_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase8_test_path_path);
    const text_phase8_test_path = try guard.readUtf8File(io, allocator, text_phase8_test_path_path);
    defer allocator.free(text_phase8_test_path);
    for (PHASE8_TEST_PATH) |marker| try guard.requireMarker(text_phase8_test_path, marker);
    const text_workflow_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_required_markers_path);
    const text_workflow_required_markers = try guard.readUtf8File(io, allocator, text_workflow_required_markers_path);
    defer allocator.free(text_workflow_required_markers);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_workflow_required_markers, marker);
    const text_validator_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_required_markers_path);
    const text_validator_required_markers = try guard.readUtf8File(io, allocator, text_validator_required_markers_path);
    defer allocator.free(text_validator_required_markers);
    for (VALIDATOR_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_validator_required_markers, marker);
    const text_phase8_test_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase8_test_required_markers_path);
    const text_phase8_test_required_markers = try guard.readUtf8File(io, allocator, text_phase8_test_required_markers_path);
    defer allocator.free(text_phase8_test_required_markers);
    for (PHASE8_TEST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_phase8_test_required_markers, marker);
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
