const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_SHARED_ROLLBACK_SUMMARY_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "DOCS_README_PATH",
    "SCRIPTS_README_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.",
    "`scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_build_only_phase12_surface.zig`, and `scripts/zigux/check_phase12_release_readiness_packet.zig` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.",
    "keep the bounded packet split explicit here too: `virtio_net` stays starter-present reviewability, `virtio_scsi` stays the smoke-first and rollback-lab packet, `nvme_pci` stays driver-local outside the shared smoke-and-test route, and the Phase 12 libbpf packet stays parked behind survey, snapshot, and verify-shard reminder surfaces instead of widening the docs root into deeper DMA, queueing, throughput, or transport claims.",
    "Phase 12 flow - the current shared release packet stays reviewable through the release-order and readiness companions, the scripts-side support checker pair, the shipped validator body, the returned shared Makefile routes, the shared build gate, and the bounded driver-family split instead of reviving a missing validate wrapper or widening into driver-local DMA, queueing, throughput, or segmented-rollout claims",
    "`Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 12 reminder packet explicit from the scripts root",
    "`zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and the shared checker pair keep the current smoke-first build gate explicit, while `virtio_net` stays starter-present reviewability, `virtio_scsi` stays the smoke-first and rollback-lab packet, and `nvme_pci` stays driver-local outside the shared smoke-and-test route",
};

const FIXTURE_TEXT = [_][]const u8{
    "# Zigux Documentation",
    "# scripts/zigux",
};

const DOCS_README_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FIXTURE_TEXT) |marker| try guard.requireMarker(text, marker);
    for (DOCS_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text, marker);
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
