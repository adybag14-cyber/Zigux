const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_SAMPLES_README_SURFACE=pass";
pub const self_test_pass_marker = "PHASE5_SAMPLES_README_SURFACE_SELF_TEST=pass";

const REQUIRED_TEXT = [_][]const u8{
    "The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:",
    "Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.",
    "Current `master` keeps the kobject sample-root port directly readable in `samples/zigux/` through `samples/zigux/kobject_example.zig`.",
    "Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.",
    "Keep the kobject anchor framed as a roadmap-backed Phase 5 target with a mixed direct-plus-public-tree-backed packet: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread returns them directly too.",
    "For the trace-events anchor, keep `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit in the same reminder packet.",
    "Keep the bounded formatting companion as the current direct cue for the approved non-runtime trace-events anchor, keep it framed as a sibling cue instead of a fifth sample, and keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route framed as public-tree-backed companion, repo-reality-gap, or historical-support references rather than direct authenticated proof.",
    "Current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; cmdline reviewability remains under `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_cmdline_survey.zig` rather than the four shipped Phase 5 samples.",
    "Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, bitmap, `printf`, `vsprintf`, or broad `format` sample families landed here as standalone samples.",
    "Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.",
};

const NO_EXTRA_SAMPLE_MARKERS = [_][]const u8{
    "* `*string*`",
    "* `*cmdline*`",
    "* `*argv*`",
    "* `*rbtree*`",
    "* `*kasprintf*`",
    "* `*strarray*`",
    "* `*bitmap*`",
    "* `*printf*`",
    "* `*vsprintf*`",
    "* `*format*`",
};

const FORBIDDEN_TEXT = [_][]const u8{
    "Do count it as a fifth approved Phase 5 anchor.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 proof.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_text_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_required_text_path);
    const text_required_text = try guard.readUtf8File(io, allocator, text_required_text_path);
    defer allocator.free(text_required_text);
    for (REQUIRED_TEXT) |marker| try guard.requireMarker(text_required_text, marker);
    const text_no_extra_sample_markers_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_no_extra_sample_markers_path);
    const text_no_extra_sample_markers = try guard.readUtf8File(io, allocator, text_no_extra_sample_markers_path);
    defer allocator.free(text_no_extra_sample_markers);
    for (NO_EXTRA_SAMPLE_MARKERS) |marker| try guard.requireMarker(text_no_extra_sample_markers, marker);
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
