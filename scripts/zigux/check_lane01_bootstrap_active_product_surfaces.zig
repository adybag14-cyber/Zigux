const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST=pass";

const SECTION_HEADING = [_][]const u8{
    "Active product surfaces",
};

const NEXT_HEADING = [_][]const u8{
    "Start here",
};

const EXPECTED_LINES = [_][]const u8{
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts\\zigux/check_lane01_bootstrap_charter_alignment.zig` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_section_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_section_heading_path);
    const text_section_heading = try guard.readUtf8File(io, allocator, text_section_heading_path);
    defer allocator.free(text_section_heading);
    for (SECTION_HEADING) |marker| try guard.requireMarker(text_section_heading, marker);
    const text_next_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_next_heading_path);
    const text_next_heading = try guard.readUtf8File(io, allocator, text_next_heading_path);
    defer allocator.free(text_next_heading);
    for (NEXT_HEADING) |marker| try guard.requireMarker(text_next_heading, marker);
    const text_expected_lines_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(text_expected_lines_path);
    const text_expected_lines = try guard.readUtf8File(io, allocator, text_expected_lines_path);
    defer allocator.free(text_expected_lines);
    for (EXPECTED_LINES) |marker| try guard.requireExactLineCount(text_expected_lines, marker, 1);
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
