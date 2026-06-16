const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_README_WINDOWS_NOTE=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST=pass";

const WINDOWS_NOTE = [_][]const u8{
    "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.",
};

const ACTIVE_PRODUCT_SURFACES_HEADING = [_][]const u8{
    "Active product surfaces",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_windows_note_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_windows_note_path);
    const text_windows_note = try guard.readUtf8File(io, allocator, text_windows_note_path);
    defer allocator.free(text_windows_note);
    for (WINDOWS_NOTE) |marker| try guard.requireMarker(text_windows_note, marker);
    const text_active_product_surfaces_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_active_product_surfaces_heading_path);
    const text_active_product_surfaces_heading = try guard.readUtf8File(io, allocator, text_active_product_surfaces_heading_path);
    defer allocator.free(text_active_product_surfaces_heading);
    for (ACTIVE_PRODUCT_SURFACES_HEADING) |marker| try guard.requireMarker(text_active_product_surfaces_heading, marker);
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
