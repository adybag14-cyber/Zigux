const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE4_ATOMIC64_WRAPPER_EVIDENCE=pass";
pub const self_test_pass_marker = "CHECK_PHASE4_ATOMIC64_WRAPPER_EVIDENCE_SELF_TEST=pass";

const PIN_LABEL = [_][]const u8{
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "# Phase 4 Gate Evidence",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "phase4-runtime-atomic64-diff-survey-tests",
    "make -C zigux phase4-runtime-atomic64-diff-survey",
};

const REQUIRED_WRAPPER_MARKERS = [_][]const u8{
    "test \"atomic64 diff wrapper keeps the shared gate-evidence packet explicit\" {",
    "test \"atomic64 diff wrapper keeps its own source inventory explicit\" {",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA={s}",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA={s}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_pin_label_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_pin_label_path);
    const text_pin_label = try guard.readUtf8File(io, allocator, text_pin_label_path);
    defer allocator.free(text_pin_label);
    for (PIN_LABEL) |marker| try guard.requireMarker(text_pin_label, marker);
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_required_wrapper_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_wrapper_markers_path);
    const text_required_wrapper_markers = try guard.readUtf8File(io, allocator, text_required_wrapper_markers_path);
    defer allocator.free(text_required_wrapper_markers);
    for (REQUIRED_WRAPPER_MARKERS) |marker| try guard.requireMarker(text_required_wrapper_markers, marker);
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
