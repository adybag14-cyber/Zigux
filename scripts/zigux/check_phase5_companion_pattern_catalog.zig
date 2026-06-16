const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_COMPANION_PATTERN_CATALOG=pass";
pub const self_test_pass_marker = "PHASE5_COMPANION_PATTERN_CATALOG_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 5 still stays inside these roadmap-backed anchors:",
    "Current `master` ships these bounded Phase 5 companion files:",
    "`samples/zigux/bytestream_fifo_window_contract.zig`",
    "`samples/zigux/kobject_example_attr_group_contract.zig`",
    "`samples/zigux/kretprobe_example_instance_budget_contract.zig`",
    "`samples/zigux/trace_events_string_formatting_sample.zig`",
    "`samples/zigux/trace_events_callback_focus_contract.zig`",
    "Keep `zigux/tests/phase5_build.zig` framed as the shared rerun companion for the wider Phase 5 packet rather than as sample-local proof.",
    "Keep `samples/zigux/runtime_*.zig` in the separate Phase 9 lane rather than using runtime files as extra Phase 5 evidence.",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "a fifth approved Phase 5 sample family",
    "runtime files are extra Phase 5 evidence",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-companion-pattern-catalog.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_forbidden_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-companion-pattern-catalog.md");
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
