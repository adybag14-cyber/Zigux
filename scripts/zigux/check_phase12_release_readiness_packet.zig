const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README_PATH",
    "FREEZE_MAP_PATH",
    "REVIEW_CHECKLIST_PATH",
    "RELEASE_READINESS_SURVEY_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_CLOSURE_CHECKLIST_PATH",
    "RELEASE_COORDINATION_MATRIX_PATH",
    "RAW_GITHUB_COVERAGE_SURVEY_PATH",
    "PHASE12_COMPLEX_DRIVER_LANE_PATH",
    "PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH",
    "CROSS_COMPILE_SMOKE_PATH",
    "SCRIPTS_README_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "COMPLEX_DRIVER_PACKET_CHECKER_PATH",
    "CROSS_COMPILE_SMOKE_CHECKER_PATH",
    "RELEASE_READINESS_CHECKER_PATH",
    "LIBBPF_SNAPSHOT_CHECKER_PATH",
    "LIBBPF_LANE_MARKER_CHECKER_PATH",
    "LIBBPF_HEAVY_CONSUMER_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "TESTS_README_PATH",
    "PHASE12_BUILD_PATH",
    "WORKFLOW_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 12 notes",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "make -C zigux phase12-validate",
    "kernel/workqueue.c",
    "net/core/skbuff.c",
    "Phase 12 reviewer prompt:",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "zig run scripts/zigux/check_phase12_complex_driver_lane_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase12_cross_compile_smoke.zig -- --self-test",
    "make -C zigux phase12-smoke",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "make -C zigux phase12-test",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "anti-overlap checker: `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`",
    "compile-smoke checker: `scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig --self-test",
    "scripts/zigux/check_phase12_cross_compile_smoke.zig --self-test",
    "current contents-bridge shared support bundle during degraded contents reads:",
    "Segmented rollout is the governing rule for the active tranche: only the six-file `virtio_net` sextet may move through the shared wrapper set, while the rollback-lab `virtio_scsi` survey-build packet, the published-but-unwired `nvme_pci` foothold, and the parked libbpf packet stay outside that shared route until new checker-backed promotions land on `master`.",
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
    "scripts/zigux/check_build_only_phase12_surface.zig",
    "zigux/tests/phase12_build.zig",
    "make -C zigux phase12-validate",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "scripts/zigux/check_phase12_release_readiness_packet.zig --self-test",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "make -C zigux phase12-validate",
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
    "make -C zigux phase12-validate",
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
    "make -C zigux phase12-smoke",
    "BUILD_ONLY_CHECKER_PATH = \"scripts/zigux/check_build_only_phase12_surface.zig\"",
    "RELEASE_READINESS_CHECKER_PATH = (",
    "PHASE12_VALIDATION=pass",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Tests-root reviewer prompt:",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "run: zig run validate_phase12.zig",
    "run: make -C zigux phase12",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const FREEZE_MAP_PATH = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const RELEASE_READINESS_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RAW_GITHUB_COVERAGE_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const PHASE12_COMPLEX_DRIVER_LANE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
};

const PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
};

const CROSS_COMPILE_SMOKE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-cross-compile-smoke.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const COMPLEX_DRIVER_PACKET_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
};

const CROSS_COMPILE_SMOKE_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
};

const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
};

const LIBBPF_SNAPSHOT_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
};

const LIBBPF_LANE_MARKER_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
};

const LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase12.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const PHASE12_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_COMPLEX_DRIVER_LANE_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH) |marker| try guard.requireMarker(text, marker);
    for (CROSS_COMPILE_SMOKE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (COMPLEX_DRIVER_PACKET_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (CROSS_COMPILE_SMOKE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_SNAPSHOT_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_LANE_MARKER_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_HEAVY_CONSUMER_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (PHASE12_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
