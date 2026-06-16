const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "`PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_STATUS=deterministic_gap_open`",
    "`make -C zigux phase11-validate` is the surviving shared Makefile route on",
    "`zigux/tests/fixtures/phase11_build_inventory.json` truthfully records the",
    "No shared Phase 11 fixture-refresh manifest currently records which simple",
    "No shared Phase 11 golden-output checker or expectation catalog currently",
    "Current `master` does not materialize `make -C zigux phase11`,",
};

const REQUIRED_CONTRACT_MARKERS = [_][]const u8{
    "`zigux/Makefile` now materializes `make -C zigux phase11-validate`",
    "`zigux/tests/phase11_build.zig` is not part of the current shared packet",
    "no shared `zigux/tests/phase11_build.zig` replay route on current `master`",
};

const REQUIRED_MATRIX_MARKERS = [_][]const u8{
    "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
    "That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`",
};

const EXPECTED_COUNTS = [_][]const u8{
    "build_test_names",
    "shared_test_depend_steps",
    "dedicated_survey_replays",
    "shared_adjunct_build_replays",
    "exact_current_checks",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_COUNTS) |marker| try guard.requireMarker(text, marker);
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
