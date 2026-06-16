const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_SAMPLES_README_RUNTIME_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "SECTION_MARKER",
    "SEQUENCING_MARKER",
    "CHECKLIST_MARKER",
    "BOUNDARY_CHECKER_MARKER",
    "TESTS_README_MARKER",
    "TRACE_EVENTS_SAMPLE_MARKER",
    "SELFTEST_HOOK_MARKER",
    "LIFECYCLE_MARKER",
    "BACKLOG_MARKER",
    "PHASE2_BOUNDARY_MARKER",
    "PHASE3_BOUNDARY_MARKER",
    "BITMAP_PHASE5_BOUNDARY_MARKER",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "`samples/zigux/runtime_bitmap.zig`",
    "`samples/zigux/runtime_bitmap_loader.zig`",
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    "phase9-runtime-bitmap-top-bit-tests",
    "make -C zigux phase9-runtime-bitmap-top-bit-test",
    "make -C zigux phase9-runtime-loader-shared-tests",
};

const SAMPLES_README_PATH = [_][]const u8{
    "samples/zigux/README.md",
};

const SECTION_MARKER = [_][]const u8{
    "## Separate Phase 9 runtime pilot family",
};

const SEQUENCING_MARKER = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
};

const CHECKLIST_MARKER = [_][]const u8{
    "`Documentation/zigux/review-checklist.md`",
};

const BOUNDARY_CHECKER_MARKER = [_][]const u8{
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
};

const TESTS_README_MARKER = [_][]const u8{
    "`zigux/tests/README.md`",
};

const TRACE_EVENTS_SAMPLE_MARKER = [_][]const u8{
    "`samples/zigux/runtime_trace_events.zig`",
};

const SELFTEST_HOOK_MARKER = [_][]const u8{
    "`.provides_selftest_hook = true`",
};

const LIFECYCLE_MARKER = [_][]const u8{
    "initialized, selftest_complete, and exited lifecycle tracking",
};

const BACKLOG_MARKER = [_][]const u8{
    "current `master` does not currently expose the broader shared runtime-loader packet",
};

const PHASE2_BOUNDARY_MARKER = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references",
};

const PHASE3_BOUNDARY_MARKER = [_][]const u8{
    "`rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence",
};

const BITMAP_PHASE5_BOUNDARY_MARKER = [_][]const u8{
    "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SAMPLES_README_PATH) |marker| try guard.requireMarker(text, marker);
    for (SECTION_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_MARKER) |marker| try guard.requireMarker(text, marker);
    for (CHECKLIST_MARKER) |marker| try guard.requireMarker(text, marker);
    for (BOUNDARY_CHECKER_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKER) |marker| try guard.requireMarker(text, marker);
    for (TRACE_EVENTS_SAMPLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (SELFTEST_HOOK_MARKER) |marker| try guard.requireMarker(text, marker);
    for (LIFECYCLE_MARKER) |marker| try guard.requireMarker(text, marker);
    for (BACKLOG_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE2_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
    for (BITMAP_PHASE5_BOUNDARY_MARKER) |marker| try guard.requireMarker(text, marker);
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
