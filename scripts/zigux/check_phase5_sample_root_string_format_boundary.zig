const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Current `master` also keeps the bounded non-runtime trace-events packet visible through the broader sample-root companion `samples/zigux/trace_events_sample.zig`, the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder packet.",
    "* `samples/zigux/trace_events_string_formatting_sample.zig` stays the direct sample-root proof for the bounded formatting companion, while `samples/zigux/trace_events_sample.zig` stays broader public-tree-backed companion evidence rather than a returned full trace-events port or a fifth sample",
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "returned full trace-events port",
    "standalone helper packet or a fifth Phase 5 sample",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_forbidden_markers_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_forbidden_markers_path);
    const text_forbidden_markers = try guard.readUtf8File(io, allocator, text_forbidden_markers_path);
    defer allocator.free(text_forbidden_markers);
    for (FORBIDDEN_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_markers, marker) != null) return guard.GuardError.MissingMarker;
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
