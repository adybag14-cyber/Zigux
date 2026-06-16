const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_READBACK_NOTE=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_READBACK_NOTE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Authenticated contents readback in this run directly returned:",
    "Fresh public current-`master` GitHub file readback still kept these owner-plus-companion packet members visible:",
    "same-lane reminder work should treat those authenticated-contents `404` results as connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo",
    "`zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route",
    "`samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c` even when the current authenticated contents route flakes on that owner path",
    "non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim",
    "`Documentation/zigux/phase5-kobject-sample-survey.md` and `Documentation/zigux/phase5-sample-lane-sequencing.md` already keep the dedicated survey note, bounded attr-group companion trio, focused replay, shared build route, and public-tree-backed owner-plus-companion split explicit.",
    "If the lane reopens now, start with `samples/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and repair only one bounded surface if it stops matching the direct survey-note plus public-tree-backed owner-and-companion split above.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are direct authenticated reminder or packet evidence again",
    "same-lane reminder work should treat those authenticated-contents `404` results as proof that the broader kobject packet vanished from the repo",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-current-readback-note.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-current-readback-note.md");
    defer allocator.free(text_forbidden_markers_path);
    const text_forbidden_markers = try guard.readUtf8File(io, allocator, text_forbidden_markers_path);
    defer allocator.free(text_forbidden_markers);
    for (FORBIDDEN_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
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
