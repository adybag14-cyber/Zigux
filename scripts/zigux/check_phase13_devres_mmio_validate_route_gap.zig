const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP=pass";

const REQUIRED_FILES = [_][]const u8{
    "NOTE_PATH",
    "README_PATH",
    "MAKEFILE_PATH",
    "TRACEABILITY_PATH",
    "LANE_PATH",
    "SLICE_PATH",
    "SURVEY_PATH",
    "MMIO_CHECKER_PATH",
};

const NOTE_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase13_devres_mmio_packet.zig`",
    "`zigux/Makefile` is present again on `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.",
    "`scripts\zigux/validate_phase13_release.zig`",
    "`scripts/zigux/check_phase13_devres_packet.zig`",
    "`scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_boundary_evidence.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`zigux/tests/phase13_build.zig`",
};

const README_MARKERS = [_][]const u8{
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    "current `master` still does not materialize `scripts\zigux/validate_phase13_release.zig`, `scripts/zigux/check_phase13_devres_packet_alignment.zig`, `scripts/zigux/check_phase13_landlock_ruleset_packet.zig`, `scripts/zigux/check_phase13_notifier_priority_signal.zig`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, and `include/zigux/notifier_abi.h`, so treat those validator-first, build, helper, header, and notifier-route companions as repo-reality gaps rather than direct scripts-root evidence",
};

const TRACEABILITY_MARKERS = [_][]const u8{
    "the historically named `scripts/zigux/check_phase13_devres_mmio_packet.zig`",
    "The `check-phase13-devres-mmio-packet.py` filename now persists as a historical handle, but on current `master` the checker fail-closes the narrower DMA-boundary, planner, and scatterlist packet rather than the older direct MMIO replay.",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
};

const LANE_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase13_devres_mmio_packet.zig`",
    "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
};

const SLICE_MARKERS = [_][]const u8{
    "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface, while the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps",
    "`scripts/zigux/check_phase13_devres_packet_alignment.zig` stays in the same repo-reality gaps bucket beside that broader direct helper packet",
};

const SURVEY_MARKERS = [_][]const u8{
    "current `master` still does not ship the broader direct helper packet that older Phase 13 lane memory described",
    "current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check_phase13_devres_packet_alignment.zig`.",
};

const MMIO_CHECKER_MARKERS = [_][]const u8{
    "SURVEY_PATH = Path(\"Documentation/zigux/phase13-devres-survey.md\")",
    "PLANNER_NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md\")",
    "SCATTERLIST_SLICE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-slice.md\")",
    "PHASE13_DEVRES_MMIO_PACKET=pass",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TRACEABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LANE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SLICE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MMIO_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
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
