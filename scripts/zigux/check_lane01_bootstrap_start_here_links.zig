const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_START_HERE_LINKS=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_START_HERE_LINKS_SELF_TEST=pass";

const START_HERE_HEADING = [_][]const u8{
    "Start here",
};

const START_HERE_LINES = [_][]const u8{
    "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "- [Live Product Docs](../Documentation/zigux/README.md)",
    "- [Review Checklist](../Documentation/zigux/review-checklist.md)",
    "- [Freeze Map](../Documentation/zigux/freeze-map.md)",
    "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_start_here_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_start_here_heading_path);
    const text_start_here_heading = try guard.readUtf8File(io, allocator, text_start_here_heading_path);
    defer allocator.free(text_start_here_heading);
    for (START_HERE_HEADING) |marker| try guard.requireMarker(text_start_here_heading, marker);
    const text_start_here_lines_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_start_here_lines_path);
    const text_start_here_lines = try guard.readUtf8File(io, allocator, text_start_here_lines_path);
    defer allocator.free(text_start_here_lines);
    for (START_HERE_LINES) |marker| try guard.requireExactLineCount(text_start_here_lines, marker, 1);
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
