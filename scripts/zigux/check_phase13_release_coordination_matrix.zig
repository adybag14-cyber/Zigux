const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass";

const GAP_PATHS = [_][]const u8{
    "scripts\zigux/validate_phase13_release.zig",
    "scripts/zigux/check_phase13_devres_packet_alignment.zig",
    "scripts/zigux/check_phase13_landlock_ruleset_packet.zig",
    "scripts/zigux/check_phase13_notifier_priority_signal.zig",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "This matrix does close the Phase 13 tranche.",
    "a shipped Makefile-backed review handle",
    "Current `master` now exposes `make -C zigux phase13-validate`",
};

const REQUIRED_MARKERS = [_][]const u8{
    "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
    "- shared-summary owner: `PMO / Release Management`",
    "- shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "- tests-root alignment companion: `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`",
    "Keep the stable contributor-facing handle distinct from this PMO coordination companion:",
    "4. `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `scripts\zigux/validate_phase13_release.zig`",
    "- `scripts/zigux/check_phase13_devres_packet_alignment.zig`",
    "- `scripts/zigux/check_phase13_landlock_ruleset_packet.zig`",
    "- `scripts/zigux/check_phase13_notifier_priority_signal.zig`",
    "This matrix does not close the Phase 13 tranche.",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces:",
    "Keep broad release wording tied to that reminder packet while the missing validator-first helpers and missing shared build route surfaces remain explicit repo-reality gaps.",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names",
    "Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` aligned as supporting shared reminder surfaces rather than as the stable contributor-facing handle itself.",
    "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase13-release-notes-survey.md`",
    "- `Documentation/zigux/phase13-roadmap-traceability.md`",
    "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "Phase 13 flow - the current scripts-root shared-helper packet stays reviewable through the stable contributor-facing handle, the shipped shared-summary guard, the tests-root alignment companion, the shipped helper-local `libfs`, `devres`, and Landlock packet anchors, and the adjacent notifier evidence",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:",
    "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
};

const MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase13-release-coordination-matrix.md",
};

const RELEASE_NOTES_PATH = [_][]const u8{
    "Documentation/zigux/phase13-release-notes-survey.md",
};

const TRACEABILITY_PATH = [_][]const u8{
    "Documentation/zigux/phase13-roadmap-traceability.md",
};

const WORKFLOW_GUIDE_PATH = [_][]const u8{
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
};

const DOCS_ROOT_PATH = [_][]const u8{
    "Documentation/zigux/README.md",
};

const SCRIPTS_ROOT_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const TESTS_ROOT_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (GAP_PATHS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_NOTES_PATH) |marker| try guard.requireMarker(text, marker);
    for (TRACEABILITY_PATH) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_GUIDE_PATH) |marker| try guard.requireMarker(text, marker);
    for (DOCS_ROOT_PATH) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_ROOT_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_ROOT_PATH) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
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
