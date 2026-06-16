const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_PERF_ROUTE_SURFACE=pass";
pub const self_test_pass_marker = "PHASE8_PERF_ROUTE_SURFACE_SELF_TEST=pass";

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const PERF_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
};

const SHARED_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_build.zig",
};

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "Validate Phase 8 tooling routes",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 exec-cmd tests",
    "Run focused Phase 8 libbpf segment tests",
    "Run Phase 8 tooling tests",
    "make -C zigux phase8-test",
};

const MAKEFILE_REQUIRED_MARKERS = [_][]const u8{
    "phase8-validate:",
    "phase8-exec-cmd-test:",
    "phase8-libbpf-segments-test:",
    "phase8-perf-buffer-poll-test:",
    "phase8-test:",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
};

const SCRIPTS_README_REQUIRED_MARKERS = [_][]const u8{
    "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`, `scripts\\zigux/check_phase8_tests_readme_alignment.zig`, `scripts\\zigux/validate_phase8.zig`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts\\zigux/validate_phase8.zig`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route",
};

const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
    "current direct-readback Phase 8 anchors:",
    "`scripts\\zigux/check_phase8_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`make -C zigux phase8-test`",
};

const PERF_BUILD_REQUIRED_MARKERS = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    "const test_step = b.step(\"test\", \"Run focused Phase 8 perf-buffer poll tests\");",
    "test_step.dependOn(&run_perf_buffer_poll_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
};

const SHARED_BUILD_REQUIRED_MARKERS = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "const test_step = b.step(\"test\", \"Run the shared Phase 8 tooling tests.\");",
    "test_step.dependOn(&run_perf_buffer_poll_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path_path);
    const text_workflow_path = try guard.readUtf8File(io, allocator, text_workflow_path_path);
    defer allocator.free(text_workflow_path);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text_workflow_path, marker);
    const text_makefile_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_makefile_path_path);
    const text_makefile_path = try guard.readUtf8File(io, allocator, text_makefile_path_path);
    defer allocator.free(text_makefile_path);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text_makefile_path, marker);
    const text_scripts_readme_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_readme_path_path);
    const text_scripts_readme_path = try guard.readUtf8File(io, allocator, text_scripts_readme_path_path);
    defer allocator.free(text_scripts_readme_path);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text_scripts_readme_path, marker);
    const text_tests_readme_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_readme_path_path);
    const text_tests_readme_path = try guard.readUtf8File(io, allocator, text_tests_readme_path_path);
    defer allocator.free(text_tests_readme_path);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text_tests_readme_path, marker);
    const text_perf_build_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_perf_build_path_path);
    const text_perf_build_path = try guard.readUtf8File(io, allocator, text_perf_build_path_path);
    defer allocator.free(text_perf_build_path);
    for (PERF_BUILD_PATH) |marker| try guard.requireMarker(text_perf_build_path, marker);
    const text_shared_build_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_shared_build_path_path);
    const text_shared_build_path = try guard.readUtf8File(io, allocator, text_shared_build_path_path);
    defer allocator.free(text_shared_build_path);
    for (SHARED_BUILD_PATH) |marker| try guard.requireMarker(text_shared_build_path, marker);
    const text_workflow_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_required_markers_path);
    const text_workflow_required_markers = try guard.readUtf8File(io, allocator, text_workflow_required_markers_path);
    defer allocator.free(text_workflow_required_markers);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_workflow_required_markers, marker);
    const text_makefile_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_makefile_required_markers_path);
    const text_makefile_required_markers = try guard.readUtf8File(io, allocator, text_makefile_required_markers_path);
    defer allocator.free(text_makefile_required_markers);
    for (MAKEFILE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_makefile_required_markers, marker);
    const text_scripts_readme_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_readme_required_markers_path);
    const text_scripts_readme_required_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_required_markers_path);
    defer allocator.free(text_scripts_readme_required_markers);
    for (SCRIPTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_required_markers, marker);
    const text_tests_readme_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_readme_required_markers_path);
    const text_tests_readme_required_markers = try guard.readUtf8File(io, allocator, text_tests_readme_required_markers_path);
    defer allocator.free(text_tests_readme_required_markers);
    for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_tests_readme_required_markers, marker);
    const text_perf_build_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_perf_build_required_markers_path);
    const text_perf_build_required_markers = try guard.readUtf8File(io, allocator, text_perf_build_required_markers_path);
    defer allocator.free(text_perf_build_required_markers);
    for (PERF_BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_perf_build_required_markers, marker);
    const text_shared_build_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_shared_build_required_markers_path);
    const text_shared_build_required_markers = try guard.readUtf8File(io, allocator, text_shared_build_required_markers_path);
    defer allocator.free(text_shared_build_required_markers);
    for (SHARED_BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_shared_build_required_markers, marker);
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
