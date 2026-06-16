const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_RBTREE_STYLE_SAMPLE_ROUTING=pass";
pub const self_test_pass_marker = "PHASE5_RBTREE_STYLE_SAMPLE_ROUTING_SELF_TEST=pass";

const REQUIRED_PATH_MARKERS = [_][]const u8{
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "samples/zigux/README.md",
    "tools/lib/rbtree.zig",
};

const REQUIRED_TEXT = [_][]const u8{
    "`PHASE5_STATUS=routing-note`",
    "`PHASE5_LANE_KEY=P5-L20`",
    "Current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample.",
    "`samples/zigux/kobject_example.zig` is the nearest live ownership-tree Phase 5 sample packet",
    "`tools/lib/rbtree.zig` remains helper-owned Phase 1 evidence rather than Phase 5 sample-root proof",
    "do not invent a fifth approved sample anchor under `samples/zigux/`",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "landed Phase 5 rbtree sample",
    "fifth approved sample anchor has landed",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_path_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-rbtree-style-sample-routing.md");
    defer allocator.free(text_required_path_markers_path);
    const text_required_path_markers = try guard.readUtf8File(io, allocator, text_required_path_markers_path);
    defer allocator.free(text_required_path_markers);
    for (REQUIRED_PATH_MARKERS) |marker| try guard.requireMarker(text_required_path_markers, marker);
    const text_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-rbtree-style-sample-routing.md");
    defer allocator.free(text_required_text_path);
    const text_required_text = try guard.readUtf8File(io, allocator, text_required_text_path);
    defer allocator.free(text_required_text);
    for (REQUIRED_TEXT) |marker| try guard.requireMarker(text_required_text, marker);
    const text_forbidden_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-rbtree-style-sample-routing.md");
    defer allocator.free(text_forbidden_text_path);
    const text_forbidden_text = try guard.readUtf8File(io, allocator, text_forbidden_text_path);
    defer allocator.free(text_forbidden_text);
    for (FORBIDDEN_TEXT) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_text, marker) != null) return guard.GuardError.MissingMarker;
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
