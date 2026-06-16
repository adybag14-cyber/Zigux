const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ROLLBACK_OWNERS=pass";
pub const self_test_pass_marker = "PHASE4_ROLLBACK_OWNERS_SELF_TEST=pass";

const SELF_TEST_MATRIX = [_][]const u8{
    "# Phase 4 Validation Matrix\n\n## Status\n  * scope: name the rollback owners for each bounded gate or survey\n\n## Lab And CI Matrix\n  * `zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`\n  * `zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`\n  * `Documentation/zigux/phase4-kprobe-example-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`\n  * `Documentation/zigux/phase4-test-fsmount-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`\n  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`\n  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`\n",
};

const SELF_TEST_REVERSIBLE_NOTE = [_][]const u8{
    "# Phase 4 Reversible Delivery Evidence\n\nCurrent direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.\n",
};

const MATRIX_MARKERS = [_][]const u8{
    "name the rollback owners for each bounded gate or survey",
    "`zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`",
    "`zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
};

const REVERSIBLE_NOTE_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates",
    "keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_matrix_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_matrix_path);
    const text_self_test_matrix = try guard.readUtf8File(io, allocator, text_self_test_matrix_path);
    defer allocator.free(text_self_test_matrix);
    for (SELF_TEST_MATRIX) |marker| try guard.requireMarker(text_self_test_matrix, marker);
    const text_self_test_reversible_note_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_reversible_note_path);
    const text_self_test_reversible_note = try guard.readUtf8File(io, allocator, text_self_test_reversible_note_path);
    defer allocator.free(text_self_test_reversible_note);
    for (SELF_TEST_REVERSIBLE_NOTE) |marker| try guard.requireMarker(text_self_test_reversible_note, marker);
    const text_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_markers_path);
    const text_matrix_markers = try guard.readUtf8File(io, allocator, text_matrix_markers_path);
    defer allocator.free(text_matrix_markers);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text_matrix_markers, marker);
    const text_reversible_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_reversible_note_markers_path);
    const text_reversible_note_markers = try guard.readUtf8File(io, allocator, text_reversible_note_markers_path);
    defer allocator.free(text_reversible_note_markers);
    for (REVERSIBLE_NOTE_MARKERS) |marker| try guard.requireMarker(text_reversible_note_markers, marker);
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
