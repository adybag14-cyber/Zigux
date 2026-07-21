const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "COORDINATION_MATRIX_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_READINESS_PATH",
    "RELEASE_CLOSURE_PATH",
    "RAW_GITHUB_COVERAGE_PATH",
    "COMPLEX_DRIVER_LANE_PATH",
    "LIBBPF_LANE_PATH",
    "CROSS_COMPILE_SMOKE_PATH",
    "FREEZE_MAP_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "READINESS_CHECKER_PATH",
    "CROSS_COMPILE_SMOKE_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "PHASE12_BUILD_PATH",
    "WORKFLOW_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "compile-smoke checker: `scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "validator-first support bundle: `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, `scripts/zigux/check_phase12_libbpf_lane_marker.zig`, `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and the shipped wrapper name `make -C zigux phase12-validate`",
    "shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`",
    "The active shared build packet is the returned six-file `virtio_net` sextet only:",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
    "`zigux/tests/phase12_virtio_net_receive_refill_replay.zig`",
    "`zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
    "`zigux/tests/phase12_virtio_net_post_reset_replay.zig`",
    "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_survey.zig`",
    "`zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check_phase12_virtio_scsi_packet.zig` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
    "Current `master` now ships the degraded-workflow evidence packet `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_libbpf_snapshot.zig`, `scripts/zigux/check_phase12_libbpf_lane_marker.zig`, `scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig`, and `scripts\zigux/validate_phase12.zig` while also shipping the `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper set.",
    "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts/zigux/check_phase12_complex_driver_lane_packet.zig`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence.",
    "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
    "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
    "the directly readable `zigux/Makefile` blob `4d572bfda15dc6ae7cd419cc4c7f858d973cda26` still prefers the repo-local `.zig-toolchain` executable",
    "before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
    "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`",
    "The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through the shared `smoke` and `test` steps",
    "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`",
    "The shipped heavy-consumer guard now sits beside that same support bundle too: `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig -- --self-test` and `zig run scripts/zigux/check_phase12_libbpf_heavy_consumer_packet.zig --` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint",
    "- support checker: `scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`",
    "current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, and `make -C zigux phase12-virtio-net-syntax-lab-test`",
    "the isolated syntax-lab rerun handles are `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all` and `make -C zigux phase12-virtio-net-syntax-lab-test`, so the companion stays reviewable without joining the shared packet",
    "the shipped cross-compile checker now keeps that returned wrapper wording plus the isolated syntax-lab rerun hook fail-closed across this note and `zigux/Makefile`",
    "- `net/core/skbuff.c`",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
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
    "\"phase12-virtio-net-survey-tests\"",
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
    "test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
    "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_survey_tests.step);",
    "- name: Self-test current Phase 12 build-only surface checker",
    "run: zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test",
    "- name: Self-test current Phase 12 release-readiness packet checker",
    "run: zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "- name: Validate current Phase 12 support bundle",
    "run: zig run scripts/zigux/validate_phase12.zig",
    "- name: Run current Phase 12 smoke packet",
    "run: make -C zigux phase12-smoke",
    "- name: Run current Phase 12 shared test packet",
    "run: make -C zigux phase12-test",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "reminder-only wrapper name `make -C zigux phase12-validate`",
    "still omitting `phase12-validate`",
    "returned five-file `virtio_net` quintet",
    "phase12: phase12-smoke phase12-test",
};

const COORDINATION_MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const RELEASE_READINESS_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RELEASE_CLOSURE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RAW_GITHUB_COVERAGE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const COMPLEX_DRIVER_LANE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
};

const LIBBPF_LANE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
};

const CROSS_COMPILE_SMOKE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-cross-compile-smoke.md",
};

const FREEZE_MAP_PATH = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
};

const CROSS_COMPILE_SMOKE_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\zigux/validate_phase12.zig",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
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
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COORDINATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_PATH) |marker| try guard.requireMarker(text, marker);
    for (COMPLEX_DRIVER_LANE_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_LANE_PATH) |marker| try guard.requireMarker(text, marker);
    for (CROSS_COMPILE_SMOKE_PATH) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (CROSS_COMPILE_SMOKE_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
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
