const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_TRACE_EVENTS_SURVEY_SURFACE=pass";
pub const self_test_pass_marker = "PHASE5_TRACE_EVENTS_SURVEY_SURFACE_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE5_STATUS=verified-public-fallback-companion-truthfulness`",
    "keep the broader non-runtime sample-local companions visible as public-tree-backed companion evidence while the contents route still misses them",
    "Fresh public current-`master` reread in this run also surfaced the broader sample-local companion paths again through their live GitHub blob pages:",
    "The shared `zigux/tests/phase5_build.zig` route should stay framed separately as returned shared build-route evidence again rather than as companion-only support vocabulary.",
    "`scripts\\zigux/check_phase5_review_guide_surface.zig` still guards the direct-proof, public-tree-backed-companion, and no-extra-sample wording",
    "the approved formatting idiom remains the selected-string plus `iter=%d` cue described in `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`",
    "bounded destination behavior remains part of the approved idiom reminder: `formatIterationMessageInto(12, [5]u8)` stays a no-space boundary, while `formatIterationMessageInto(12, [7]u8)` stays the success-sized `iter=12` case",
};

const APPROVED_IDIOM_MARKERS = [_][]const u8{
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`",
};

const SAMPLE_ROOT_MARKERS = [_][]const u8{
    "Current `master` also keeps the bounded non-runtime trace-events packet visible through the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig` together with the shared Phase 5 reminder packet.",
    "Keep that trace-events packet framed as the approved selected-string plus `iter=%d` formatting idiom for the Phase 5 anchor:",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as the direct non-runtime kretprobe tests-root packet, and keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
    const text_approved_idiom_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_approved_idiom_markers_path);
    const text_approved_idiom_markers = try guard.readUtf8File(io, allocator, text_approved_idiom_markers_path);
    defer allocator.free(text_approved_idiom_markers);
    for (APPROVED_IDIOM_MARKERS) |marker| try guard.requireMarker(text_approved_idiom_markers, marker);
    const text_sample_root_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_sample_root_markers_path);
    const text_sample_root_markers = try guard.readUtf8File(io, allocator, text_sample_root_markers_path);
    defer allocator.free(text_sample_root_markers);
    for (SAMPLE_ROOT_MARKERS) |marker| try guard.requireMarker(text_sample_root_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
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
