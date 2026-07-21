const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_RELEASE_PACKET_INDEX_SELF_TEST=pass";

const EXPECTED_GAPS = [_][]const u8{
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
};

const REQUIRED_MARKERS = [_][]const u8{
    "This note is the compact PMO packet index for the active Phase 13 shared-helper release packet.",
    "- lane owner: `pmo-release`",
    "- `Documentation/zigux/phase13-release-packet-index.md`",
    "- `scripts/zigux/check_phase13_roadmap_traceability.zig`",
    "- `scripts\zigux/validate_phase13_release.zig`",
    "No shared Phase 13 build handle is returned on current `master`.",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
    "- `zigux/tests/phase13_build.zig`",
    "This index is a coordination artifact, not a closure claim.",
    "then land only the smallest reminder-side truthfulness repair and rerun `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`, `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`, `zig run scripts/zigux/check_phase13_roadmap_traceability.zig --`, and `zig run scripts/zigux/validate_phase13_release.zig`.",
    "release-packet index companion: `Documentation/zigux/phase13-release-packet-index.md`",
    "4. `Documentation/zigux/phase13-release-packet-index.md`",
    "`Documentation/zigux/phase13-release-packet-index.md`",
    "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
    "Current `master` also now materializes `scripts/zigux/check_phase13_roadmap_traceability.zig`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.",
    "- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`",
    "2. Reread the Phase 13 destination packet next through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `scripts\zigux/validate_phase13_release.zig`, `scripts/zigux/check_phase13_shared_summary_surfaces.zig`, and `scripts/zigux/check_phase13_tests_readme_alignment.zig`.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "This index does close the Phase 13 tranche.",
    "This index does imply a shipped shared Makefile route for Phase 13.",
};

const INDEX_PATH = [_][]const u8{
    "Documentation/zigux/phase13-release-packet-index.md",
};

const MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase13-release-coordination-matrix.md",
};

const NOTES_PATH = [_][]const u8{
    "Documentation/zigux/phase13-release-notes-survey.md",
};

const TRACEABILITY_PATH = [_][]const u8{
    "Documentation/zigux/phase13-roadmap-traceability.md",
};

const HANDOFF_PATH = [_][]const u8{
    "Documentation/zigux/phase12-phase13-release-handoff.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (INDEX_PATH) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (NOTES_PATH) |marker| try guard.requireMarker(text, marker);
    for (TRACEABILITY_PATH) |marker| try guard.requireMarker(text, marker);
    for (HANDOFF_PATH) |marker| try guard.requireMarker(text, marker);
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
