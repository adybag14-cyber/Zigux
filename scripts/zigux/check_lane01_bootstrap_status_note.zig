const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_STATUS_NOTE=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_STATUS_NOTE_SELF_TEST=pass";

const ROADMAP_REL = [_][]const u8{
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
};

const STATUS_NOTE_LINES = [_][]const u8{
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
};

const ORDERED_HEADINGS = [_][]const u8{
    "## Purpose",
    "## Bootstrap Status Note",
    "## Inputs Reviewed",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_roadmap_rel_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_roadmap_rel_path);
    const text_roadmap_rel = try guard.readUtf8File(io, allocator, text_roadmap_rel_path);
    defer allocator.free(text_roadmap_rel);
    for (ROADMAP_REL) |marker| try guard.requireMarker(text_roadmap_rel, marker);
    const text_status_note_lines_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_status_note_lines_path);
    const text_status_note_lines = try guard.readUtf8File(io, allocator, text_status_note_lines_path);
    defer allocator.free(text_status_note_lines);
    for (STATUS_NOTE_LINES) |marker| try guard.requireExactLineCount(text_status_note_lines, marker, 1);
    const text_ordered_headings_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_ordered_headings_path);
    const text_ordered_headings = try guard.readUtf8File(io, allocator, text_ordered_headings_path);
    defer allocator.free(text_ordered_headings);
    for (ORDERED_HEADINGS) |marker| try guard.requireMarker(text_ordered_headings, marker);
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
