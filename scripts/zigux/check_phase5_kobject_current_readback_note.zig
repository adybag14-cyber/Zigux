const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_CURRENT_READBACK_NOTE=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_CURRENT_READBACK_NOTE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Authenticated contents readback in this run directly returned:",
    "Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.",
    "The same run still confirmed these current `master` packet members through public GitHub file readback:",
    "the direct sample-root file, focused tests-root replay, shared build route, and attr-group companion are readable through the authenticated contents route used here",
    "the dedicated survey note, manifest-backed contract, and survey replay remain visible on public current `master` even though this run's authenticated contents route returned `404` for those three packet members",
    "same-lane reminder work should treat those authenticated-contents `404` results as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo",
    "The same slot then compared the broader shared Phase 5 reminder packet against this note and found that most shared reminder surfaces had already caught up to the narrower kobject split recorded here. `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now keep the direct sample-root file, focused tests-root replay, direct shared build-route companion, public-tree-backed survey note and manifest companions, and bounded attr-group companion aligned with this note.",
    "Fresh Phase 5 reread on 2026-05-22 also confirms that the formerly lagging checklist-plus-guard pair has now caught up to the same split. `Documentation/zigux/review-checklist.md` and `scripts\\zigux/check_phase5_review_guide_surface.zig` now keep the survey note, manifest-backed contract, and survey replay framed as current public-tree-backed companion evidence while leaving `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_build.zig`, and `samples/zigux/kobject_example_attr_group_contract.zig` explicit as the directly readable packet members in this runtime.",
    "That means this dedicated note no longer needs to hand off a checklist-only repair as the next default follow-through. The remaining same-lane posture is simply to keep future shared-surface wording anchored to this split if another reminder surface drifts.",
    "1. reread this note beside the exact shared surface that looks stale and confirm whether the direct sample-root file, focused tests-root replay, shared build-route companion, bounded attr-group companion, and public-tree-backed survey companions are still described with the same split",
    "If the lane reopens, compare this note against the exact shared Phase 5 surface that drifted and repair only that one bounded surface.",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-current-readback-note.md");
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
