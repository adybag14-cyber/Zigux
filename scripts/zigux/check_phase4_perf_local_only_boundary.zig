const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_LOCAL_ONLY_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=pass";

const MANIFEST_MARKERS = [_][]const u8{
    "\"shared_ci_perf_promotion_status\": \"pending\"",
    "\"bootstrap_ci_posture\": \"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\"",
    "\"dedicated_local_survey_wrapper\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"",
    "\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"",
};

const VALIDATOR_REQUIRED_MARKERS = [_][]const u8{
    "CheckSpec(\"phase4-perf-baseline-packet-self-test\", (\"python\", \"scripts\\zigux/check_phase4_perf_baseline_packet.zig\", \"--self-test\"))",
    "CheckSpec(\"phase4-perf-baseline-packet\", (\"python\", \"scripts\\zigux/check_phase4_perf_baseline_packet.zig\"))",
    "CheckSpec(\"phase4-perf-threshold-matrix-self-test\", (\"python\", \"scripts\\zigux/check_phase4_perf_threshold_matrix.zig\", \"--self-test\"))",
    "CheckSpec(\"phase4-perf-threshold-matrix\", (\"python\", \"scripts\\zigux/check_phase4_perf_threshold_matrix.zig\"))",
};

const VALIDATOR_FORBIDDEN_MARKERS = [_][]const u8{
    "CheckSpec(\"phase4-perf-baseline-survey\",",
    "(\"zig\", \"build\", \"phase4-perf-baseline-survey\", \"--build-file\", \"zigux/tests/phase4_build.zig\")",
};

const MAKEFILE_REQUIRED_MARKERS = [_][]const u8{
    "phase4-validate:",
    "phase4-perf-baseline-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_baseline_packet.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_perf_threshold_matrix.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
};

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
};

const WORKFLOW_FORBIDDEN_MARKERS = [_][]const u8{
    "run: make -C zigux phase4-perf-baseline-survey",
    "run: zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
};

const BUILD_REQUIRED_MARKERS = [_][]const u8{
    "\"phase4-perf-baseline-survey-tests\"",
    "\"phase4-perf-baseline-survey\",",
    "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);",
};

const BUILD_FORBIDDEN_MARKERS = [_][]const u8{
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_manifest_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_perf_baseline_manifest.json");
    defer allocator.free(text_manifest_markers_path);
    const text_manifest_markers = try guard.readUtf8File(io, allocator, text_manifest_markers_path);
    defer allocator.free(text_manifest_markers);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text_manifest_markers, marker);
    const text_validator_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_required_markers_path);
    const text_validator_required_markers = try guard.readUtf8File(io, allocator, text_validator_required_markers_path);
    defer allocator.free(text_validator_required_markers);
    for (VALIDATOR_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_validator_required_markers, marker);
    const text_validator_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_validator_forbidden_markers_path);
    const text_validator_forbidden_markers = try guard.readUtf8File(io, allocator, text_validator_forbidden_markers_path);
    defer allocator.free(text_validator_forbidden_markers);
    for (VALIDATOR_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_validator_forbidden_markers, marker);
    const text_makefile_required_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_required_markers_path);
    const text_makefile_required_markers = try guard.readUtf8File(io, allocator, text_makefile_required_markers_path);
    defer allocator.free(text_makefile_required_markers);
    for (MAKEFILE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_makefile_required_markers, marker);
    const text_workflow_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_required_markers_path);
    const text_workflow_required_markers = try guard.readUtf8File(io, allocator, text_workflow_required_markers_path);
    defer allocator.free(text_workflow_required_markers);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_workflow_required_markers, marker);
    const text_workflow_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_forbidden_markers_path);
    const text_workflow_forbidden_markers = try guard.readUtf8File(io, allocator, text_workflow_forbidden_markers_path);
    defer allocator.free(text_workflow_forbidden_markers);
    for (WORKFLOW_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_workflow_forbidden_markers, marker);
    const text_build_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_build_required_markers_path);
    const text_build_required_markers = try guard.readUtf8File(io, allocator, text_build_required_markers_path);
    defer allocator.free(text_build_required_markers);
    for (BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_build_required_markers, marker);
    const text_build_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_build_forbidden_markers_path);
    const text_build_forbidden_markers = try guard.readUtf8File(io, allocator, text_build_forbidden_markers_path);
    defer allocator.free(text_build_forbidden_markers);
    for (BUILD_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_build_forbidden_markers, marker);
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
