const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_PMO_SHARED_SURFACE_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README_PATH",
    "REVIEW_CHECKLIST_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_READINESS_PATH",
    "RELEASE_CLOSURE_PATH",
    "RELEASE_COORDINATION_PATH",
    "RAW_GITHUB_COVERAGE_PATH",
    "SCRIPTS_README_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "READINESS_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "TESTS_README_PATH",
    "PHASE12_BUILD_PATH",
    "WORKFLOW_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 12 notes",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, and `scripts/zigux/check_phase12_release_readiness_packet.zig` keep the directly readable validator-side support bundle explicit",
    "`scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`",
    "`zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again",
    "shared-summary lane owner: `pmo-release`",
    "Current repo-reality override: the route story on current `master` is now fully returned rather than split.",
    "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
    "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
    "shared-summary lane owner: `pmo-release`",
    "The active shared build route on current `master` is the six-file `virtio_net` smoke-and-test packet in `zigux/tests/phase12_build.zig`",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    "support checker: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    "shared-summary lane owner: `pmo-release`",
    "validator-first support bundle: `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "The active shared build packet is the returned six-file `virtio_net` sextet only:",
    "- exact current support-bundle reread checked on `2026-05-26`:",
    "`scripts/zigux/check_phase12_release_readiness_packet.zig` `4a10382b6d897afccad318bdeccbb959a6373087`",
    "`zigux/Makefile` `4d572bfda15dc6ae7cd419cc4c7f858d973cda26`",
    "`zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c`",
    "`scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, and `scripts/zigux/check_phase12_release_readiness_packet.zig` keep the directly readable validator-side support bundle explicit",
    "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    "BUILD_ONLY_CHECKER_PATH = \"scripts/zigux/check_build_only_phase12_surface.zig\"",
    "RELEASE_READINESS_CHECKER_PATH = (",
    "PHASE12_VALIDATION=pass",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check_build_only_phase12_surface.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, `scripts\zigux/validate_phase12.zig`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route.",
    "phase12_virtio_net_queue_resume",
    "phase12_virtio_net_receive_refill_replay",
    "phase12_virtio_net_transmit_recycle",
    "phase12_virtio_net_post_reset_replay",
    "phase12_virtio_net_throughput_parity",
    "phase12_virtio_net_survey",
    "Self-test current Phase 12 release-readiness packet checker",
    "zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test",
    "Validate current Phase 12 support bundle",
    "zig run scripts/zigux/validate_phase12.zig",
    "Run current Phase 12 aggregate route",
    "make -C zigux phase12",
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

const RELEASE_READINESS_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RELEASE_CLOSURE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const RELEASE_COORDINATION_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RAW_GITHUB_COVERAGE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
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
    for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_COORDINATION_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
