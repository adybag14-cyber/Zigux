const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_ARGV_SPLIT_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass";

const EXPECTED_MANIFEST_ANCHOR = [_][]const u8{
    "lib/argv_split.c",
};

const EXPECTED_MANIFEST_STATE = [_][]const u8{
    "helper_slice_test_fixture_survey_manifest_anchor",
};

const EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = [_][]const u8{
    "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet, and reopen only when a fresh reread finds the next checker-, manifest-, slice-note-, or fixture-vector drift inside that packet before widening into any new vector-backed replay proof.",
};

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/phase7-argv-split-slice.md",
    "lib/argv_split.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "samples/zigux/README.md",
};

const EXPECTED_COVERED_HELPERS = [_][]const u8{
    "countArgc",
    "argvSplit",
    "argvSplitWithArgc",
    "argvFree",
    "ArgvSplitResult.deinit",
    "ArgvSplitResult.cArgv",
};

const EXPECTED_OWNERSHIP_FOCUS = [_][]const u8{
    "argvSplit() duplicates the caller input before tokenizing so returned tokens stay inside helper-owned storage",
    "countArgc(), cStringPrefix(), nextArgSpan(), and nextSplitArgSpan() keep token counting and separator zeroing bounded to the exported C-string prefix",
    "blank-input results reuse exported empty storage and argv sentinel views without widening beyond the returned packet",
    "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL",
    "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins",
    "blank, whitespace-only, whitespace-before-first-NUL, and leading-NUL inputs all reuse the same shared empty storage, argv, and cArgv() views across calls so blank-result teardown stays repeatable without hidden allocation churn",
    "non-blank sibling results keep owned storage, argv slices, and exported cArgv views isolated across calls",
    "deinit(), argvFree(), allocator-failure cleanup, and overflow rejection keep release ownership explicit without widening beyond the returned argv packet",
    "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership",
    "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership",
    "the no-standalone-argv sample boundary stays explicit only while `samples/zigux/README.md` keeps `*argv*` listed among the no-extra-sample reminders",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-argv-split-slice_md = [_][]const u8{
    "`PHASE7_STATUS=helper_local_test_packet_landed`",
    "`PHASE7_SLICE=argv-split-runtime-leaf`",
    "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
    "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned fixture-backed packet.",
    "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet, and reopen only when a fresh reread finds the next checker-, manifest-, slice-note-, or fixture-vector drift inside that packet before widening into any new vector-backed replay proof.",
    "whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space",
    "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins",
    "blank, whitespace-only, whitespace-before-first-NUL, and leading-NUL inputs all reuse the same shared empty storage, argv, and `cArgv()` views across calls, so blank-result teardown stays repeatable without hidden allocation churn",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-argv-split-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    "PHASE7_ARGV_SPLIT_PACKET=pass",
    "PHASE7_ARGV_SPLIT_PACKET=fail",
    "MISSING_PHASE7_ARGV_SPLIT_FILES_START",
    "MISSING_PHASE7_ARGV_SPLIT_FILES_END",
    "MISSING_PHASE7_ARGV_SPLIT_MARKERS_START",
    "MISSING_PHASE7_ARGV_SPLIT_MARKERS_END",
    "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\",",
    "EXPECTED_MANIFEST_LANE_KEY = \"P7-L09\"",
    "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
    "EXPECTED_MANIFEST_ANCHOR = \"lib/argv_split.c\"",
    "EXPECTED_MANIFEST_STATE = \"helper_slice_test_fixture_survey_manifest_anchor\"",
    "EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (",
    "EXPECTED_REVIEW_SURFACES = [",
    "EXPECTED_COVERED_HELPERS = [",
    "EXPECTED_OWNERSHIP_FOCUS = [",
    "MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_START",
    "MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_END",
};

const REQUIRED_MARKERS__lib_argv_split_zig = [_][]const u8{
    "pub const ArgvSplitResult = struct {",
    "pub fn countArgc(",
    "pub fn argvSplit(",
    "pub fn argvSplitWithArgc(",
    "pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {",
    "pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {",
    "fn nextSplitArgSpan(",
    "test \"argvSplit treats whitespace before the first NUL as blank input\" {",
    "test \"argvSplit treats a leading NUL as blank input\" {",
    "test \"argvSplit reuses shared blank sentinel views without argc output\" {",
    "test \"blank-input deinit on one caller keeps the shared sentinel views usable for another\" {",
    "test \"argvFree resets released non-blank results to the shared empty exported views\" {",
    "test \"non-blank argvSplit results keep caller-owned teardown isolated across siblings\" {",
    "test \"argv_split aliases preserve helper-local count, split, and free behavior\" {",
    "test \"argvSplit reports overflow before sizing the null-terminated argv vector\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_argv_split_zig = [_][]const u8{
    "const argv_split = @import(\"argv_split\");",
    "const fixture_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");",
    "test \"phase 7 argv split companion replays copied-storage token ownership\" {",
    "test \"phase 7 argv split companion replays non-blank cross-call ownership independence\" {",
    "test \"phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation\" {",
    "test \"phase 7 argv split companion replays repeated blank-result sentinel reuse\" {",
    "test \"phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse\" {",
    "test \"phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries\" {",
    "test \"phase 7 argv split companion replays caller-owned teardown and failure boundaries\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_argv_split_manifest_json = [_][]const u8{
    "\"anchor\": \"lib/argv_split.c\"",
    "\"current_master_state\": \"helper_slice_test_fixture_survey_manifest_anchor\"",
    "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"",
    "fixture-backed helper-local survey-manifest-checker truthfulness packet",
    "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL",
    "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins",
    "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership",
    "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership",
};

const REQUIRED_MARKERS__zigux_tests_phase7_argv_split_survey_zig = [_][]const u8{
    "test \"phase 7 argv split survey keeps the returned fixture-backed helper-local packet truthful\" {",
    "try std.testing.expectEqualStrings(\"helper_slice_test_fixture_survey_manifest_anchor\", manifest.current_master_state);",
    "const fixture_vectors = try readRepoFile(allocator, fixture_path);",
    "try std.testing.expect(!stringSliceContains(manifest.review_surfaces, \"Documentation/zigux/phase7-helper-lane-sequencing.md\"));",
    "try expectNotContains(checker, \"\\\"Documentation/zigux/phase7-helper-lane-sequencing.md\\\",\");",
    "try expectContains(helper, \"test \\\"argvSplit treats whitespace before the first NUL as blank input\\\" {\");",
    "try expectContains(helper, \"test \\\"argvSplit reuses shared blank sentinel views without argc output\\\" {\");",
    "try expectContains(helper, \"test \\\"argvSplit reports overflow before sizing the null-terminated argv vector\\\" {\");",
    "try expectContains(helper_companion, \"phase 7 argv split companion replays repeated blank-result sentinel reuse\");",
    "try expectContains(helper_companion, \"phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse\");",
    "try expectContains(helper_companion, \"phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries\");",
    "try expectContains(fixture_vectors, \"whitespace_before_first_nul_reuses_empty_packet\");",
    "try expectContains(slice_note, \"leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins\");",
    "try expectStringSliceContains(manifest.ownership_focus, \"leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins\");",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase7_argv_split_vectors_zig = [_][]const u8{
    "pub const ArgvSplitVector = struct {",
    "pub const phase7_argv_split_vectors = [_]ArgvSplitVector{",
    "copied_storage_whitespace_packet",
    "blank_input_reuses_empty_packet",
    "whitespace_before_first_nul_reuses_empty_packet",
    "leading_nul_reuses_empty_packet",
    "first_nul_truncation_keeps_tail_outside_packet",
    "quoted_tokens_stay_whitespace_split",
};

const REQUIRED_MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` still ships no standalone Phase 5 sample-root files here for:",
    "* `*argv*`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_manifest_anchor_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_manifest_anchor_path);
    const text_expected_manifest_anchor = try guard.readUtf8File(io, allocator, text_expected_manifest_anchor_path);
    defer allocator.free(text_expected_manifest_anchor);
    for (EXPECTED_MANIFEST_ANCHOR) |marker| try guard.requireMarker(text_expected_manifest_anchor, marker);
    const text_expected_manifest_state_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_manifest_state_path);
    const text_expected_manifest_state = try guard.readUtf8File(io, allocator, text_expected_manifest_state_path);
    defer allocator.free(text_expected_manifest_state);
    for (EXPECTED_MANIFEST_STATE) |marker| try guard.requireMarker(text_expected_manifest_state, marker);
    const text_expected_manifest_next_bounded_step_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_manifest_next_bounded_step_path);
    const text_expected_manifest_next_bounded_step = try guard.readUtf8File(io, allocator, text_expected_manifest_next_bounded_step_path);
    defer allocator.free(text_expected_manifest_next_bounded_step);
    for (EXPECTED_MANIFEST_NEXT_BOUNDED_STEP) |marker| try guard.requireMarker(text_expected_manifest_next_bounded_step, marker);
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_expected_covered_helpers_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_covered_helpers_path);
    const text_expected_covered_helpers = try guard.readUtf8File(io, allocator, text_expected_covered_helpers_path);
    defer allocator.free(text_expected_covered_helpers);
    for (EXPECTED_COVERED_HELPERS) |marker| try guard.requireMarker(text_expected_covered_helpers, marker);
    const text_expected_ownership_focus_path = try guard.joinPath(allocator, root, "lib/argv_split.c");
    defer allocator.free(text_expected_ownership_focus_path);
    const text_expected_ownership_focus = try guard.readUtf8File(io, allocator, text_expected_ownership_focus_path);
    defer allocator.free(text_expected_ownership_focus);
    for (EXPECTED_OWNERSHIP_FOCUS) |marker| try guard.requireMarker(text_expected_ownership_focus, marker);
    const text_required_markers__documentation_zigux_phase7-argv-split-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-argv-split-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-argv-split-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-argv-split-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-argv-split-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-argv-split-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-argv-split-slice_md, marker);
    const text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_argv_split_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-argv-split-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-argv-split-packet_py, marker);
    const text_required_markers__lib_argv_split_zig_path = try guard.joinPath(allocator, root, "lib/argv_split.zig");
    defer allocator.free(text_required_markers__lib_argv_split_zig_path);
    const text_required_markers__lib_argv_split_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_argv_split_zig_path);
    defer allocator.free(text_required_markers__lib_argv_split_zig);
    for (REQUIRED_MARKERS__lib_argv_split_zig) |marker| try guard.requireMarker(text_required_markers__lib_argv_split_zig, marker);
    const text_required_markers__zigux_tests_phase7_argv_split_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_zig_path);
    const text_required_markers__zigux_tests_phase7_argv_split_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_argv_split_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_argv_split_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_argv_split_zig, marker);
    const text_required_markers__zigux_tests_phase7_argv_split_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_argv_split_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_argv_split_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_argv_split_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_argv_split_manifest_json, marker);
    const text_required_markers__zigux_tests_phase7_argv_split_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_argv_split_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_argv_split_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_argv_split_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_argv_split_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_argv_split_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_argv_split_survey_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig_path);
    const text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase7_argv_split_vectors_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase7_argv_split_vectors_zig, marker);
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
