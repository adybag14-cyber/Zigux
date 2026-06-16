const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_TESTS_README_LIBBPF_ANCHOR_SELF_TEST=pass";

const LIBBPF_SNAPSHOT_DETERMINISM_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
};

const REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
    "`scripts/zigux/check_phase12_release_readiness_packet.zig`",
    "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const LIBBPF_SNAPSHOT_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (LIBBPF_SNAPSHOT_DETERMINISM_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text, marker);
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
