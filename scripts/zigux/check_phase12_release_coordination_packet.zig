const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_RELEASE_COORDINATION_PACKET_SELF_TEST=pass";

const RELEASE_COORDINATION_MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RAW_GITHUB_COVERAGE_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const RELEASE_READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
};

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README_PATH",
    "REVIEW_CHECKLIST_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_COORDINATION_MATRIX_PATH",
    "RELEASE_CLOSURE_CHECKLIST_PATH",
    "RAW_GITHUB_COVERAGE_SURVEY_PATH",
    "SCRIPTS_README_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "RELEASE_READINESS_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "TESTS_README_PATH",
    "PHASE12_BUILD_PATH",
    "WORKFLOW_PATH",
};

const VIRTIO_NET_SEXTET = [_][]const u8{
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
};

const REQUIRED_MARKERS = [_][]const u8{
    "- `Documentation/zigux/phase12-release-sequencing.md`",
    "- `Documentation/zigux/phase12-release-readiness-survey.md`",
    "- `Documentation/zigux/phase12-release-closure-checklist.md`",
    "- `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`",
    "`Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`",
    "shared wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "shared wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "shared wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "shared wrapper evidence on current `master`: `make -C zigux phase12`",
    "The active smoke-first direct shard set on current `master` is",
    "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path",
    "- shared-summary lane owner: `pmo-release`",
    "- validator-first support bundle: `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "- shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`",
    "The active shared build packet is the returned six-file `virtio_net` sextet only:",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check_phase12_virtio_scsi_packet.zig` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
    "- lane owner: `pmo-release`",
    "The directly readable validator-first support bundle still reruns as `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`",
    "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
    "The current driver-local `virtio_scsi` split must stay explicit too: current `master` keeps the dedicated `Documentation/zigux/phase12-virtio-scsi-slice.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` pair together with `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    "- current contents-bridge shared support bundle during degraded contents reads:",
    "- `zigux/tests/phase12_build.zig`",
    "- `scripts/zigux/check_build_only_phase12_surface.zig`",
    "- `zigux/Makefile`",
    "`scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, and `scripts/zigux/check_phase12_release_readiness_packet.zig` keep the directly readable validator-side support bundle explicit from the scripts root",
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared Phase 12 packet",
    "BUILD_ONLY_CHECKER_PATH",
    "RELEASE_READINESS_CHECKER_PATH",
    "PHASE12_VALIDATION=pass",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps",
    "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route",
    "- name: Self-test current Phase 12 release-readiness packet checker",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "- name: Validate current Phase 12 support bundle",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const REVIEW_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/review-checklist.md",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
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
    for (RELEASE_COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (VIRTIO_NET_SEXTET) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
