const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_SHARED_SAMPLE_GUIDANCE=pass";
pub const self_test_pass_marker = "PHASE5_SHARED_SAMPLE_GUIDANCE_SELF_TEST=pass";

const GUIDE_MARKERS = [_][]const u8{
    "* `samples/kfifo/bytestream-example.c`",
    "* `samples/kobject/kobject-example.c`",
    "* `samples/kprobes/kretprobe_example.c`",
    "* `samples/trace_events/trace-events-sample.c`",
    "Repeated current-run GitHub-app contents reads for `scripts/zigux/README.md` still returned `Not Found`, so keep that older scripts-root reminder out of the current shared-surface inventory until a fresh reread proves the exact path returned again.",
    "Keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary",
};

const SAMPLES_README_MARKERS = [_][]const u8{
    "* `samples/zigux/bytestream_fifo.zig`",
    "* `samples/zigux/kobject_example.zig`",
    "* `samples/zigux/kretprobe_example.zig`",
    "* `samples/zigux/trace_events_sample.zig`",
    "Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.",
    "current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample.",
    "current public-tree-backed companion evidence rather than direct authenticated-contents proof",
};

const TESTS_README_MARKERS = [_][]const u8{
    "* `Documentation/zigux/phase5-kfifo-sample-survey.md`",
    "* `zigux/tests/phase5_bytestream_fifo_manifest.json`",
    "* `Documentation/zigux/phase5-kobject-sample-survey.md`",
    "* `zigux/tests/phase5_kobject_example_manifest.json`",
    "* `Documentation/zigux/phase5-kretprobe-sample-survey.md`",
    "* `zigux/tests/phase5_kretprobe_example_manifest.json`",
    "* `Documentation/zigux/phase5-trace-events-sample-survey.md`",
    "* `zigux/tests/phase5_trace_events_sample_manifest.json`",
    "* current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_guide_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_guide_markers_path);
    const text_guide_markers = try guard.readUtf8File(io, allocator, text_guide_markers_path);
    defer allocator.free(text_guide_markers);
    for (GUIDE_MARKERS) |marker| try guard.requireMarker(text_guide_markers, marker);
    const text_samples_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_samples_readme_markers_path);
    const text_samples_readme_markers = try guard.readUtf8File(io, allocator, text_samples_readme_markers_path);
    defer allocator.free(text_samples_readme_markers);
    for (SAMPLES_README_MARKERS) |marker| try guard.requireMarker(text_samples_readme_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
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
