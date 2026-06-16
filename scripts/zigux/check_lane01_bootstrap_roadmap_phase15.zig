const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_ROADMAP_PHASE15=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_ROADMAP_PHASE15_SELF_TEST=pass";

const PREVIOUS_HEADING = [_][]const u8{
    "## Phase 14: Core-Adjacent Bounded Internals",
};

const SECTION_HEADING = [_][]const u8{
    "## Phase 15: Full-Parity Blockers and Long-Term Governance",
};

const NEXT_HEADING = [_][]const u8{
    "## Freeze Map for Near- and Mid-Term Planning",
};

const EXPECTED_LINES = [_][]const u8{
    "Primary product goal:",
    "- govern the final mixed-language steady state honestly",
    "Primary Linux anchors:",
    "- `kernel/sched/core.c`",
    "- `mm/page_alloc.c`",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "Required Zigux features:",
    "- freeze map",
    "- Architecture Council review process",
    "- parity scorecard",
    "- policy for code that remains in C indefinitely",
    "This phase is about discipline, not bravado.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_previous_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_previous_heading_path);
    const text_previous_heading = try guard.readUtf8File(io, allocator, text_previous_heading_path);
    defer allocator.free(text_previous_heading);
    for (PREVIOUS_HEADING) |marker| try guard.requireMarker(text_previous_heading, marker);
    const text_section_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_section_heading_path);
    const text_section_heading = try guard.readUtf8File(io, allocator, text_section_heading_path);
    defer allocator.free(text_section_heading);
    for (SECTION_HEADING) |marker| try guard.requireMarker(text_section_heading, marker);
    const text_next_heading_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(text_next_heading_path);
    const text_next_heading = try guard.readUtf8File(io, allocator, text_next_heading_path);
    defer allocator.free(text_next_heading);
    for (NEXT_HEADING) |marker| try guard.requireMarker(text_next_heading, marker);
    const text_expected_lines_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
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
