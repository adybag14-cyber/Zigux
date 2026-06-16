const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE5_SAMPLE_ROOT_TRACE_EVENTS_BOUNDARY_SELF_TEST=pass";

const REQUIRED_TEXT = [_][]const u8{
    "For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
    "Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly.",
    "Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.",
    "For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet.",
    "Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.",
    "Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "For the trace-events anchor, current `master` now keeps the direct non-runtime sample packet readable through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`",
    "Keep the direct sample, focused replay, manifest, and survey replay as the current direct packet proof",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_text_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_required_text_path);
    const text_required_text = try guard.readUtf8File(io, allocator, text_required_text_path);
    defer allocator.free(text_required_text);
    for (REQUIRED_TEXT) |marker| try guard.requireMarker(text_required_text, marker);
    const text_forbidden_text_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
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
