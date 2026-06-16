const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_CMDLINE_SURVEY_BUILD_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_CMDLINE_SURVEY_BUILD_PACKET_SELF_TEST=pass";

const EXPECTED_REVIEW_SURFACE = [_][]const u8{
    "zigux/tests/phase7_cmdline_survey_build.zig",
};

const EXPECTED_ANCHOR = [_][]const u8{
    "lib/cmdline.c",
};

const EXPECTED_STATE = [_][]const u8{
    "helper_slice_test_survey_manifest_checker_anchor",
};

const EXPECTED_NEXT_STEP = [_][]const u8{
    "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof while shared-control routes stay parked outside this helper-local lane.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-helper-lane-sequencing_md = [_][]const u8{
    "- `zigux/tests/phase7_cmdline_survey.zig`",
    "- `zigux/tests/phase7_cmdline_manifest.json`",
    "- `scripts\\zigux/check_phase7_cmdline_packet.zig`",
    "cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-cmdline-slice_md = [_][]const u8{
    "`PHASE7_LANE_KEY=P7-L08`",
    "`zigux/tests/phase7_cmdline_survey_build.zig`",
    "`zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig`",
    "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
};

const REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"phase7_cmdline_survey.zig\")",
    ".name = \"phase7-cmdline-survey\"",
    "\"phase7-cmdline-survey\"",
    "\"Run the Phase 7 cmdline survey anchor from the shared tests root\"",
    "step.dependOn(&run.step);",
};

const REQUIRED_MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` still ships no standalone Phase 5 sample-root files here for:",
    "* `*cmdline*`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_review_surface_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(text_expected_review_surface_path);
    const text_expected_review_surface = try guard.readUtf8File(io, allocator, text_expected_review_surface_path);
    defer allocator.free(text_expected_review_surface);
    for (EXPECTED_REVIEW_SURFACE) |marker| try guard.requireMarker(text_expected_review_surface, marker);
    const text_expected_anchor_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(text_expected_anchor_path);
    const text_expected_anchor = try guard.readUtf8File(io, allocator, text_expected_anchor_path);
    defer allocator.free(text_expected_anchor);
    for (EXPECTED_ANCHOR) |marker| try guard.requireMarker(text_expected_anchor, marker);
    const text_expected_state_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(text_expected_state_path);
    const text_expected_state = try guard.readUtf8File(io, allocator, text_expected_state_path);
    defer allocator.free(text_expected_state);
    for (EXPECTED_STATE) |marker| try guard.requireMarker(text_expected_state, marker);
    const text_expected_next_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(text_expected_next_step_path);
    const text_expected_next_step = try guard.readUtf8File(io, allocator, text_expected_next_step_path);
    defer allocator.free(text_expected_next_step);
    for (EXPECTED_NEXT_STEP) |marker| try guard.requireMarker(text_expected_next_step, marker);
    const text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path);
    const text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-helper-lane-sequencing_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md, marker);
    const text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-cmdline-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-cmdline-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-cmdline-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-cmdline-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-cmdline-slice_md, marker);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7/cmdline/survey/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig, marker);
    const text_required_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README/md");
    defer allocator.free(text_required_markers__samples_zigux_readme_md_path);
    const text_required_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_required_markers__samples_zigux_readme_md);
    for (REQUIRED_MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__samples_zigux_readme_md, marker);
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
