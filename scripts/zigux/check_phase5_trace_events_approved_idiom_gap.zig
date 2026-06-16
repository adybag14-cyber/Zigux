const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP=pass";
pub const self_test_pass_marker = "PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:",
    "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, and the current lane reread now returns that path directly again. Keep it framed as returned shared build-route evidence rather than as part of the broader sample-local companion set.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\\\"iter=12\\\"` and keeps the sample in `.initialized`.",
    "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue, the exact `checked_focus` review order, or the shipped guide-surface guard.",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_phase5_review_guide_surface.zig",
    "zigux/tests/README.md",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
