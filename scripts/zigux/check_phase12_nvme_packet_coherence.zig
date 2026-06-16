const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "MANIFEST_PATH",
    "SHARED_BUILD_PATH",
    "DIRECT_BUILD_PATH",
    "SURVEY_BUILD_PATH",
    "MAKEFILE_PATH",
    "GOVERNANCE_PATH",
    "FALLBACK_MAP_PATH",
};

const DIRECT_ROUTE_MARKERS = [_][]const u8{
    "phase12-nvme-pci-direct-tests",
    "phase12-nvme-pci-verify-test",
    "phase12-nvme-pci-replay-wrapper-test",
    "phase12-nvme-pci-direct-test",
};

const SURVEY_ROUTE_MARKERS = [_][]const u8{
    "phase12-nvme-pci-survey-tests",
    "phase12-nvme-pci-survey-test",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase12-nvme-pci-direct-test:",
    "$(ZIG_REPO_ROOT) build phase12-nvme-pci-direct-test --build-file zigux/tests/phase12_nvme_pci_build.zig --summary all",
    "phase12-nvme-pci-survey-test:",
    "$(ZIG_REPO_ROOT) build phase12-nvme-pci-survey-test --build-file zigux/tests/phase12_nvme_pci_survey_build.zig --summary all",
};

const GOVERNANCE_MARKERS = [_][]const u8{
    "stays outside the shared `phase12-smoke`, `phase12-test`, and aggregate `phase12` route",
    "`make -C zigux phase12-nvme-pci-direct-test`",
    "`make -C zigux phase12-nvme-pci-survey-test`",
};

const FALLBACK_MAP_MARKERS = [_][]const u8{
    "Base raw URL prefix:",
    "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/",
    "starter shard raw path: `drivers/nvme/host/pci.zig`",
    "verifier shard raw path: `drivers/nvme/host/pci_verify.zig`",
    "direct replay raw path: `zigux/tests/phase12_nvme_pci.zig`",
    "dedicated direct-build raw path: `zigux/tests/phase12_nvme_pci_build.zig`",
    "survey-build raw path: `zigux/tests/phase12_nvme_pci_survey_build.zig`",
    "slice note raw path: `Documentation/zigux/phase12-nvme-pci-slice.md`",
    "survey note raw path: `Documentation/zigux/phase12-nvme-pci-survey.md`",
    "survey gate raw path: `zigux/tests/phase12_nvme_pci_survey.zig`",
    "manifest anchor raw path: `zigux/tests/phase12_nvme_pci_manifest.json`",
    "reopen-governance raw path: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`",
    "packet checker raw path: `scripts/zigux/check_phase12_nvme_pci_packet.zig`",
    "build-only checker raw path: `scripts/zigux/check_build_only_phase12_surface.zig`",
    "cross-compile smoke checker raw path: `scripts/zigux/check_phase12_cross_compile_smoke.zig`",
    "release-readiness checker raw path: `scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "validator raw path: `scripts\zigux/validate_phase12.zig`",
    "scripts-root reminder raw path: `scripts/zigux/README.md`",
    "workflow raw path: `.github/workflows/zigux-bootstrap.yml`",
    "shared build raw path: `zigux/tests/phase12_build.zig`",
    "shared route owner raw path: `zigux/Makefile`",
};

const FORBIDDEN_SHARED_BUILD_MARKERS = [_][]const u8{
    "phase12_nvme_pci.zig",
    "phase12-nvme-pci-direct-test",
    "phase12-nvme-pci-survey-test",
    "drivers/nvme/host/pci.zig",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_NVME_PACKET_COHERENCE",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (DIRECT_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (GOVERNANCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FALLBACK_MAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_SHARED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
