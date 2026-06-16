const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_CMDLINE_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_CMDLINE_PACKET_SELF_TEST=pass";

const EXPECTED_MANIFEST_ANCHOR = [_][]const u8{
    "lib/cmdline.c",
};

const EXPECTED_MANIFEST_STATE = [_][]const u8{
    "helper_slice_test_survey_manifest_checker_anchor",
};

const EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = [_][]const u8{
    "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof while shared-control routes stay parked outside this helper-local lane.",
};

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/phase7_cmdline_survey_build.zig",
    "scripts\\zigux/check_phase7_cmdline_packet.zig",
    "samples/zigux/README.md",
};

const EXPECTED_COVERED_HELPERS = [_][]const u8{
    "parseOptionStr",
    "parse_option_str",
    "getOption",
    "get_option",
    "getOptions",
    "get_options",
    "nextArg",
    "next_arg",
    "memparse",
};

const EXPECTED_OWNERSHIP_FOCUS = [_][]const u8{
    "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix",
    "getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior",
    "the dedicated `get_option` alias replay keeps leading-plus and range-style cursor movement explicit beside the primary `getOption()` entry point",
    "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
    "nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track",
    "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
    "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
    "the no-standalone-cmdline sample boundary stays explicit only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-helper-lane-sequencing_md = [_][]const u8{
    "Documentation/zigux/phase7-cmdline-slice.md",
    "samples/zigux/README.md",
    "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`",
    "Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-build-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-cmdline-slice_md = [_][]const u8{
    "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`",
    "`PHASE7_SLICE=cmdline-runtime-leaf`",
    "`PHASE7_LANE_KEY=P7-L08`",
    "`zigux/tests/phase7_cmdline_survey_build.zig`",
    "`scripts\\zigux/check_phase7_cmdline_packet.zig`",
    "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.",
    "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
    "including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs",
    "`nextArg()` also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track",
    "dedicated `getOption()` and `get_option` cursor replay across leading-plus and range-style inputs so alias-only call sites stay reviewable beside the primary helper entry point",
    "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig",
};

const REQUIRED_MARKERS__lib_cmdline_zig = [_][]const u8{
    "pub fn parseOptionStr",
    "pub const parse_option_str = parseOptionStr;",
    "pub fn getOption",
    "pub const get_option = getOption;",
    "pub fn getOptions",
    "pub const get_options = getOptions;",
    "pub fn nextArg",
    "pub const next_arg = nextArg;",
    "pub fn memparse",
    "test \"nextArg keeps whitespace-only input as an empty sentinel before the first NUL\" {",
    "test \"nextArg keeps leading equals tokens as bare parameters\" {",
    "test \"nextArg keeps quoted leading equals tokens as bare parameters\" {",
    "test \"nextArg parses bare parameters and keeps the remaining text\" {",
    "test \"nextArg keeps quoted empty values explicit without swallowing the next token\" {",
    "test \"nextArg keeps unterminated quoted values inside the current token\" {",
    "test \"nextArg keeps rest and remaining as the same borrowed suffix view\" {",
    "test \"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\" {",
    "test \"getOptions expands negative ranges and negative upper bounds\" {",
    "test \"memparse saturates signed overflow instead of trapping\" {",
    "test \"memparse keeps leading-plus incomplete hex and no-digit fallbacks reviewable\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_cmdline_zig = [_][]const u8{
    "const cmdline = @import(\"cmdline\");",
    "test \"phase 7 cmdline companion replays exact bare-option matching boundaries\" {",
    "try std.testing.expect(!cmdline.parseOptionStr(\"quiet,debug\\x00,nohlt\", \"nohlt\"));",
    "try std.testing.expect(cmdline.parseOptionStr(\"debug,,quiet\", \"\"));",
    "try std.testing.expect(!cmdline.parseOptionStr(\"debug,\", \"\"));",
    "test \"phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture\" {",
    "test \"phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries\" {",
    "try std.testing.expectEqualStrings(\"2,9\", descending_rest);",
    "test \"phase 7 cmdline companion replays negative range expansion and negative upper-bound posture\" {",
    "test \"phase 7 cmdline companion replays validator-only getOption cursor movement\" {",
    "test \"phase 7 cmdline companion replays get_option alias cursor parity\" {",
    "test \"phase 7 cmdline companion replays quoted argument splitting and memparse boundaries\" {",
    "test \"phase 7 cmdline companion replays leading-plus fallback boundaries\" {",
    "test \"phase 7 cmdline companion replays memparse signed clamp saturation\" {",
    "test \"phase 7 cmdline companion replays borrowed nextArg suffix ownership\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_zig = [_][]const u8{
    "try std.testing.expectEqualStrings(\"helper_slice_test_survey_manifest_checker_anchor\", manifest.current_master_state);",
    "try expectContains(checker, \"PHASE7_CMDLINE_PACKET=pass\");",
    "try expectContains(slice_note, \"including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs\");",
    "try expectContains(sequencing_note, \"Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-build-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.\");",
    "try expectContains(helper, \"test \\\\\\\"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\\\\\\\" {\");",
    "try expectContains(helper_companion, \"phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries\");",
};

const REQUIRED_MARKERS__zigux_tests_phase7_cmdline_manifest_json = [_][]const u8{
    "\"current_master_state\": \"helper_slice_test_survey_manifest_checker_anchor\"",
    "\"zigux/tests/phase7_cmdline_survey_build.zig\"",
    "\"scripts\\zigux/check_phase7_cmdline_packet.zig\"",
    "\"parseOptionStr\"",
    "\"memparse\"",
    "helper-local survey-manifest-checker truthfulness packet",
    "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig",
};

const REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_build_zig = [_][]const u8{
    "phase7_cmdline_survey.zig",
    "phase7-cmdline-survey",
    "Run the Phase 7 cmdline survey anchor from the shared tests root",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-cmdline-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_CMDLINE_PACKET_SELF_TEST=pass",
    "PHASE7_CMDLINE_PACKET=pass",
    "PHASE7_CMDLINE_PACKET=fail",
    "MISSING_PHASE7_CMDLINE_FILES_START",
    "MISSING_PHASE7_CMDLINE_FILES_END",
    "MISSING_PHASE7_CMDLINE_MARKERS_START",
    "MISSING_PHASE7_CMDLINE_MARKERS_END",
    "MISMATCHED_PHASE7_CMDLINE_COUNTS_START",
    "MISMATCHED_PHASE7_CMDLINE_COUNTS_END",
    "\"Documentation/zigux/phase7-cmdline-slice.md\",",
    "\"lib/cmdline.zig\",",
    "\"zigux/tests/phase7_cmdline_survey_build.zig\",",
    "EXPECTED_MANIFEST_LANE_KEY = \"P7-L08\"",
    "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
    "EXPECTED_MANIFEST_ANCHOR = \"lib/cmdline.c\"",
    "EXPECTED_MANIFEST_STATE = \"helper_slice_test_survey_manifest_checker_anchor\"",
    "EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (",
    "EXPECTED_REVIEW_SURFACES = [",
    "EXPECTED_COVERED_HELPERS = [",
    "EXPECTED_OWNERSHIP_FOCUS = [",
    "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
};

const REQUIRED_MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` still ships no standalone Phase 5 sample-root files here for:",
    "* `*cmdline*`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_manifest_anchor_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_manifest_anchor_path);
    const text_expected_manifest_anchor = try guard.readUtf8File(io, allocator, text_expected_manifest_anchor_path);
    defer allocator.free(text_expected_manifest_anchor);
    for (EXPECTED_MANIFEST_ANCHOR) |marker| try guard.requireMarker(text_expected_manifest_anchor, marker);
    const text_expected_manifest_state_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_manifest_state_path);
    const text_expected_manifest_state = try guard.readUtf8File(io, allocator, text_expected_manifest_state_path);
    defer allocator.free(text_expected_manifest_state);
    for (EXPECTED_MANIFEST_STATE) |marker| try guard.requireMarker(text_expected_manifest_state, marker);
    const text_expected_manifest_next_bounded_step_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_manifest_next_bounded_step_path);
    const text_expected_manifest_next_bounded_step = try guard.readUtf8File(io, allocator, text_expected_manifest_next_bounded_step_path);
    defer allocator.free(text_expected_manifest_next_bounded_step);
    for (EXPECTED_MANIFEST_NEXT_BOUNDED_STEP) |marker| try guard.requireMarker(text_expected_manifest_next_bounded_step, marker);
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_expected_covered_helpers_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_covered_helpers_path);
    const text_expected_covered_helpers = try guard.readUtf8File(io, allocator, text_expected_covered_helpers_path);
    defer allocator.free(text_expected_covered_helpers);
    for (EXPECTED_COVERED_HELPERS) |marker| try guard.requireMarker(text_expected_covered_helpers, marker);
    const text_expected_ownership_focus_path = try guard.joinPath(allocator, root, "lib/cmdline.c");
    defer allocator.free(text_expected_ownership_focus_path);
    const text_expected_ownership_focus = try guard.readUtf8File(io, allocator, text_expected_ownership_focus_path);
    defer allocator.free(text_expected_ownership_focus);
    for (EXPECTED_OWNERSHIP_FOCUS) |marker| try guard.requireMarker(text_expected_ownership_focus, marker);
    const text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path);
    const text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-helper-lane-sequencing_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-helper-lane-sequencing_md, marker);
    const text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-cmdline-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-cmdline-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-cmdline-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-cmdline-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-cmdline-slice_md, marker);
    const text_required_markers__lib_cmdline_zig_path = try guard.joinPath(allocator, root, "lib/cmdline.zig");
    defer allocator.free(text_required_markers__lib_cmdline_zig_path);
    const text_required_markers__lib_cmdline_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_cmdline_zig_path);
    defer allocator.free(text_required_markers__lib_cmdline_zig);
    for (REQUIRED_MARKERS__lib_cmdline_zig) |marker| try guard.requireMarker(text_required_markers__lib_cmdline_zig, marker);
    const text_required_markers__zigux_tests_phase7_cmdline_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_zig_path);
    const text_required_markers__zigux_tests_phase7_cmdline_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_cmdline_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_cmdline_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_cmdline_zig, marker);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_cmdline_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_cmdline_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_cmdline_survey_zig, marker);
    const text_required_markers__zigux_tests_phase7_cmdline_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_cmdline_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_cmdline_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_cmdline_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_cmdline_manifest_json, marker);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_cmdline_survey_build.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path);
    const text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_cmdline_survey_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_cmdline_survey_build_zig, marker);
    const text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_cmdline_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-cmdline-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-cmdline-packet_py, marker);
    const text_required_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
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
