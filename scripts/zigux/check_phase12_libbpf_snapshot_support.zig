const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_LIBBPF_SNAPSHOT_SUPPORT_SELF_TEST=pass";

const RELEASE_READINESS_MARKERS = [_][]const u8{
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` remains the public anchor",
    "parked libbpf reviewability packet",
    "the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` remain note-owned or snapshot-backed boundaries",
};

const TESTS_README_MARKERS = [_][]const u8{
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
};

const BUILD_ONLY_CHECKER_MARKERS = [_][]const u8{
    "PHASE12_LIBBPF_SNAPSHOT_PATH = \"zigux/tests/fixtures/phase12_libbpf_snapshot.json\"",
};

const REQUIRED_FILES = [_][]const u8{
    "SNAPSHOT_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "RELEASE_READINESS_PATH",
    "TESTS_README_PATH",
};

const EXPECTED_SNAPSHOT = [_][]const u8{
    "lane_key",
    "P12-L16",
    "phase",
    "Phase 12",
    "surveyed_commit",
    "e6a4246ac3d9f4d19b91554067e821075f543448",
    "tracked_file_count",
    "tracked_paths",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "supporting_notes",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const SNAPSHOT_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const RELEASE_READINESS_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (RELEASE_READINESS_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SNAPSHOT) |marker| try guard.requireMarker(text, marker);
    for (SNAPSHOT_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
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
