const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_LIBBPF_READINESS_SNAPSHOT_SELF_TEST=pass";

const LIBBPF_SNAPSHOT_DETERMINISM_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
};

const REQUIRED_FILES = [_][]const u8{
    "RELEASE_READINESS_SURVEY_PATH",
    "RELEASE_CLOSURE_CHECKLIST_PATH",
    "LIBBPF_VERIFY_SHARD_NOTE_PATH",
    "LIBBPF_SNAPSHOT_CHECKER_PATH",
    "LIBBPF_SNAPSHOT_PATH",
    "LIBBPF_SNAPSHOT_DETERMINISM_PATH",
};

const REQUIRED_MARKERS = [_][]const u8{
    "the parked verify-shard note still governs the shared libbpf packet",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.",
    "The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.",
    "snapshot checker: `scripts/zigux/check_phase12_libbpf_snapshot.zig`",
    "snapshot anchor: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout",
    "SNAPSHOT_PATH = Path(\"zigux/tests/fixtures/phase12_libbpf_snapshot.json\")",
    "EXPECTED_LANE_KEY = \"P12-Y04\"",
    "EXPECTED_PHASE = \"Phase 12\"",
};

const SNAPSHOT_EXPECTATIONS = [_][]const u8{
    "lane_key",
    "P12-Y04",
    "phase",
    "Phase 12",
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

const SNAPSHOT_DETERMINISM_EXPECTATIONS = [_][]const u8{
    "lane_key",
    "P12-L17",
    "phase",
    "Phase 12",
    "tracked_file_count",
    "tracked_paths",
    "tools/lib/bpf/zigux_segments/pin_path.zig",
};

const RELEASE_READINESS_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

const RELEASE_CLOSURE_CHECKLIST_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const LIBBPF_VERIFY_SHARD_NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
};

const LIBBPF_SNAPSHOT_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_libbpf_snapshot.zig",
};

const LIBBPF_SNAPSHOT_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (LIBBPF_SNAPSHOT_DETERMINISM_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SNAPSHOT_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
    for (SNAPSHOT_DETERMINISM_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_CHECKLIST_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_VERIFY_SHARD_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_SNAPSHOT_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
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
