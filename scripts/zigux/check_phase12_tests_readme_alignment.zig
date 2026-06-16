const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
};

const COMPLEX_DRIVER_LANE_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_complex_driver_lane_packet.zig",
};

const CROSS_COMPILE_SMOKE_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
};

const LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig",
};

const VIRTIO_NET_RECEIVE_REFILL_REPLAY_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
};

const VIRTIO_NET_TRANSMIT_RECYCLE_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
};

const VIRTIO_NET_POST_RESET_REPLAY_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
};

const VIRTIO_NET_THROUGHPUT_PARITY_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
};

const REQUIRED_FILES = [_][]const u8{
    "TESTS_README_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_READINESS_SURVEY_PATH",
    "RELEASE_CLOSURE_CHECKLIST_PATH",
    "RELEASE_COORDINATION_MATRIX_PATH",
    "RAW_GITHUB_COVERAGE_PATH",
    "REVIEW_CHECKLIST_PATH",
    "SCRIPTS_README_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "RELEASE_READINESS_CHECKER_PATH",
    "COMPLEX_DRIVER_LANE_CHECKER_PATH",
    "CROSS_COMPILE_SMOKE_CHECKER_PATH",
    "LIBBPF_SNAPSHOT_CHECKER_PATH",
    "LIBBPF_LANE_MARKER_CHECKER_PATH",
    "LIBBPF_HEAVY_CONSUMER_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "BUILD_PATH",
    "WORKFLOW_PATH",
    "VIRTIO_NET_QUEUE_RESUME_PATH",
    "VIRTIO_NET_RECEIVE_REFILL_REPLAY_PATH",
    "VIRTIO_NET_TRANSMIT_RECYCLE_PATH",
    "VIRTIO_NET_POST_RESET_REPLAY_PATH",
    "VIRTIO_NET_THROUGHPUT_PARITY_PATH",
    "VIRTIO_NET_SURVEY_PATH",
    "VIRTIO_SCSI_SURVEY_PATH",
    "VIRTIO_SCSI_MANIFEST_PATH",
    "VIRTIO_SCSI_SURVEY_ZIG_PATH",
    "VIRTIO_SCSI_SURVEY_BUILD_PATH",
    "NVME_SURVEY_PATH",
    "NVME_MANIFEST_PATH",
    "LIBBPF_SEGMENT_SURVEY_PATH",
    "LIBBPF_VERIFY_SHARD_NOTE_PATH",
    "LIBBPF_SNAPSHOT_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "## Phase 12 shared release packet",
    "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, `scripts/zigux/check_phase12_libbpf_lane_marker.zig`, `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, `scripts\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
    "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
    "Tests-root reviewer prompt:",
    "`zigux/tests/README.md`",
    "then rerun `zig run scripts/zigux/check_build_only_phase12_surface.zig --` before widening PMO release wording.",
    "`zigux/tests/README.md`",
    "The next honest same-lane follow-through is therefore reminder-side only: leave the shared release notes parked unless `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` still understate the directly readable support bundle",
    "`zigux/tests/README.md`",
    "The next honest same-lane follow-through is therefore reminder-side only: leave this checklist parked unless `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, or `zigux/tests/README.md` understates the directly readable support bundle",
    "`zigux/tests/README.md`",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "`zigux/tests/README.md`",
    "`zigux/tests/phase12_build.zig`",
    "`scripts/zigux/check_build_only_phase12_surface.zig`",
    "Phase 12 reviewer prompt:",
    "`zigux/tests/phase12_virtio_scsi_manifest.json`",
    "`zigux/tests/phase12_virtio_scsi_survey.zig`",
    "`zigux/Makefile`",
    "current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again",
    "## Phase 12",
    "`scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "\"phase12_virtio_net_queue_resume.zig\"",
    "\"phase12_virtio_net_receive_refill_replay.zig\"",
    "\"phase12_virtio_net_transmit_recycle.zig\"",
    "\"phase12_virtio_net_post_reset_replay.zig\"",
    "\"phase12_virtio_net_throughput_parity.zig\"",
    "\"phase12_virtio_net_survey.zig\"",
    "run: zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "run: make -C zigux phase12",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const RELEASE_READINESS_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RAW_GITHUB_COVERAGE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const LIBBPF_SNAPSHOT_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
};

const LIBBPF_LANE_MARKER_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase12.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_build.zig",
};

const WORKFLOW_PATH = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const VIRTIO_NET_QUEUE_RESUME_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
};

const VIRTIO_NET_SURVEY_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_net_survey.zig",
};

const VIRTIO_SCSI_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
};

const VIRTIO_SCSI_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_manifest.json",
};

const VIRTIO_SCSI_SURVEY_ZIG_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_survey.zig",
};

const VIRTIO_SCSI_SURVEY_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
};

const NVME_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-nvme-pci-survey.md",
};

const NVME_MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase12_nvme_pci_manifest.json",
};

const LIBBPF_SEGMENT_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
};

const LIBBPF_VERIFY_SHARD_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
};

const LIBBPF_SNAPSHOT_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (COMPLEX_DRIVER_LANE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (CROSS_COMPILE_SMOKE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_HEAVY_CONSUMER_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_RECEIVE_REFILL_REPLAY_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_TRANSMIT_RECYCLE_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_POST_RESET_REPLAY_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_THROUGHPUT_PARITY_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_SNAPSHOT_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_LANE_MARKER_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_QUEUE_RESUME_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_SCSI_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_SCSI_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_SCSI_SURVEY_ZIG_PATH) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_SCSI_SURVEY_BUILD_PATH) |marker| try guard.requireMarker(text, marker);
    for (NVME_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (NVME_MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_SEGMENT_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_VERIFY_SHARD_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_SNAPSHOT_PATH) |marker| try guard.requireMarker(text, marker);
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
