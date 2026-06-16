const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_STRING_HELPERS_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass";

const EXPECTED_MANIFEST_LANE_KEY = [_][]const u8{
    "helper-local",
};

const EXPECTED_MANIFEST_ANCHOR = [_][]const u8{
    "lib/string_helpers.c",
};

const EXPECTED_MANIFEST_STATE = [_][]const u8{
    "expanded_starter_packet",
};

const EXPECTED_DIRECT_REPO_ANCHOR = [_][]const u8{
    "lib/string_helpers.zig",
};

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "scripts\\zigux/check_phase7_string_helpers_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "lib/string_helpers.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_format_boundary.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "samples/zigux/README.md",
};

const EXPECTED_COVERED_HELPERS = [_][]const u8{
    "skipSpaces",
    "skip_spaces",
    "trimSpaces",
    "strim",
    "sysfsStreq",
    "sysfs_streq",
    "matchString",
    "match_string",
    "sysfsMatchString",
    "__sysfs_match_string",
    "stringIsTerminated",
    "string_is_terminated",
    "stringGetSize",
    "string_get_size",
    "stringUnescape",
    "string_unescape",
    "stringUnescapeInplace",
    "string_unescape_inplace",
    "stringUnescapeAny",
    "string_unescape_any",
    "stringUnescapeAnyInplace",
    "string_unescape_any_inplace",
    "stringEscapeMem",
    "string_escape_mem",
    "stringEscapeMemAnyNp",
    "string_escape_mem_any_np",
    "stringEscapeStr",
    "string_escape_str",
    "stringEscapeStrAnyNp",
    "string_escape_str_any_np",
    "kasprintfStrarray",
    "kasprintf_strarray",
    "kfreeStrarray",
    "kfree_strarray",
    "kstrdupAndReplace",
    "kstrdup_and_replace",
    "kstrdupQuotable",
    "kstrdup_quotable",
    "kstrdupQuotableFile",
    "kstrdup_quotable_file",
    "kstrdupQuotableCmdline",
    "kstrdup_quotable_cmdline",
    "parseIntArray",
    "parse_int_array",
    "stringUpper",
    "string_upper",
    "stringLower",
    "string_lower",
    "memcpyAndPad",
    "memcpy_and_pad",
    "strreplace",
};

const DEVM_FOLLOW_ON_MARKER = [_][]const u8{
    "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons",
};

const NEXT_BOUNDED_STEP_MARKER = [_][]const u8{
    "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons",
};

const FULL_FAMILY_GAP_MARKER = [_][]const u8{
    "the broader full-family packet that still leaves `parse_int_array_user()` and `devm_kasprintf_strarray()` outside the current `master` helper packet",
};

const NO_EXTRA_SAMPLE_BULLETS = [_][]const u8{
    "* `*string*`",
    "* `*cmdline*`",
    "* `*argv*`",
    "* `*rbtree*`",
    "* `*kasprintf*`",
    "* `*strarray*`",
    "* `*printf*`",
    "* `*vsprintf*`",
};

const NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER = [_][]const u8{
    "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned",
};

const FORMAT_BOUNDARY_MARKER = [_][]const u8{
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.",
};

const FORMAT_BOUNDARY_FOCUS = [_][]const u8{
    "dedicated format-boundary replay for the trace-events formatting companion and broad-format exclusion",
};

const CMDLINE_OWNERSHIP_MARKER = [_][]const u8{
    "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping",
};

const TERMINATION_OWNERSHIP_MARKER = [_][]const u8{
    "stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix",
};

const EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = [_][]const u8{
    "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons, and reopen only when one of those helper-local non-goals lands or the no-sample boundary drifts on current `master`.",
};

const MANIFEST_LANE_KEY_MARKER = [_][]const u8{
    "\"lane_key\": \"helper-local\"",
};

const MANIFEST_PHASE_MARKER = [_][]const u8{
    "\"phase\": \"Phase 7\"",
};

const MANIFEST_ANCHOR_MARKER = [_][]const u8{
    "\"anchor\": \"lib/string_helpers.c\"",
};

const MANIFEST_STATE_MARKER = [_][]const u8{
    "\"current_master_state\": \"expanded_starter_packet\"",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-string-helpers-slice_md = [_][]const u8{
    "`PHASE7_STATUS=starter_landed`",
    "`scripts\\zigux/check_phase7_string_helpers_packet.zig`",
    "quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path",
    "`stringUpper()`, `string_upper()`, `stringLower()`, and `string_lower()` keep case-conversion writes inside caller-provided destination storage and stop at the exported C-string boundary",
    "quoted cmdline duplication that collapses trailing NULs",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass",
    "print(\"PHASE7_STRING_HELPERS_PACKET=pass\")",
    "print(\"PHASE7_STRING_HELPERS_PACKET=fail\")",
    "\"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\",",
    "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\",",
    "\"zigux/tests/phase7_string_helpers_format_boundary.zig\",",
    "\"lib/string_helpers.zig\": [",
    "\"pub fn devmKasprintfStrarray(\"",
    "\"pub fn devm_kasprintf_strarray(\"",
    "\"pub fn parseIntArrayUser(\"",
    "\"pub fn parse_int_array_user(\"",
    "\"zigux/tests/phase7_string_helpers_manifest.json\": [",
    "\"\\\\\\\"devmKasprintfStrarray\\\\\\\"\"",
    "\"\\\\\\\"devm_kasprintf_strarray\\\\\\\"\"",
    "\"\\\\\\\"parseIntArrayUser\\\\\\\"\"",
    "\"\\\\\\\"parse_int_array_user\\\\\\\"\"",
    "\"* `*printf*`\"",
    "\"* `*vsprintf*`\"",
    "EXPECTED_MANIFEST_LANE_KEY = \"helper-local\"",
    "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
    "EXPECTED_MANIFEST_ANCHOR = \"lib/string_helpers.c\"",
    "EXPECTED_MANIFEST_STATE = \"expanded_starter_packet\"",
    "EXPECTED_MANIFEST_OWNERSHIP_FOCUS = [",
    "EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (",
    "MISSING_PHASE7_STRING_HELPERS_FILES_START",
    "MISSING_PHASE7_STRING_HELPERS_FILES_END",
    "MISSING_PHASE7_STRING_HELPERS_MARKERS_START",
    "MISSING_PHASE7_STRING_HELPERS_MARKERS_END",
    "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START",
    "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END",
    "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START",
    "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass",
    "print(\"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass\")",
    "print(\"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=fail\")",
    "\"zigux/tests/phase7_string_helpers_format_boundary.zig\",",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_START",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_END",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_START",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_END",
};

const REQUIRED_MARKERS__lib_string_helpers_zig = [_][]const u8{
    "pub fn kasprintfStrarray(",
    "pub fn kstrdupQuotable(",
    "pub fn kstrdup_quotable(",
    "pub fn kstrdupQuotableFile(",
    "pub fn kstrdup_quotable_file(",
    "pub fn kstrdupQuotableCmdline(",
    "pub fn kstrdup_quotable_cmdline(",
    "pub fn parseIntArray(",
    "pub fn parse_int_array(",
    "pub fn stringIsTerminated(",
    "pub fn string_is_terminated(",
    "pub fn stringUpper(",
    "pub fn string_upper(",
    "pub fn stringLower(",
    "pub fn string_lower(",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_zig = [_][]const u8{
    "test \"phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix\" {",
    "test \"phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit\" {",
    "test \"phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators\" {",
    "test \"phase 7 string helpers starter keeps termination checks bounded by the caller limit\" {",
    "test \"phase 7 string helpers starter reports empty parse-int-array input as no entry\" {",
    "test \"phase 7 string helpers starter reports parse-int-array allocation failure cleanly\" {",
    "test \"phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup\" {",
    "test \"phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view\" {",
    "test \"phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested\" {",
    "test \"phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes\" {",
    "test \"phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result\" {",
    "test \"phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent\" {",
    "test \"phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary\" {",
    "test \"phase 7 string helpers starter reports kstrdupQuotable allocation failure cleanly\" {",
    "test \"phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly\" {",
    "test \"phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly\" {",
    "test \"phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly\" {",
    "test \"phase 7 string helpers starter pads bounded copies without reading past the provided source slice\" {",
    "test \"phase 7 string helpers starter replaces bytes only inside the exported c-string prefix\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_manifest_json = [_][]const u8{
    "\"scripts\\zigux/check_phase7_string_helpers_packet.zig\"",
    "\"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\"",
    "\"zigux/tests/phase7_string_helpers_format_boundary.zig\"",
    "quoted file-path duplication with explicit missing-file fallback and quotable escaping for already-materialized path strings",
    "bounded uppercase and lowercase copies through the exported C-string boundary",
    "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters",
    "dedicated helper-local checker-backed packet reviewability",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_survey_zig = [_][]const u8{
    "const checker = try readRepoFile(allocator, \"scripts\\zigux/check_phase7_string_helpers_packet.zig\");",
    "try expectContains(checker, \"PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass\");",
    "try expectContains(checker, \"* `*printf*`\");",
    "try expectContains(checker, \"* `*vsprintf*`\");",
    "const format_boundary_checker = try readRepoFile(allocator, \"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\");",
    "const format_boundary = try readRepoFile(allocator, \"zigux/tests/phase7_string_helpers_format_boundary.zig\");",
    "try expectContains(sample_boundary, \"Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.\");",
    "try expectContains(manifest, \"\\\\\\\\\"scripts\\zigux/check_phase7_string_helpers_packet.zig\\\\\\\\\"\");",
    "try expectContains(manifest, \"dedicated helper-local checker-backed packet reviewability\");",
    "try expectContains(manifest, \"kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping\");",
    "try expectContains(manifest, \"\\\\\\\\\"next_bounded_step\\\\\\\\\": \\\\\\\\\"Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons\\\\\\\\\"\");",
    "try expectContains(sample_boundary, \"Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons\");",
    "try expectContains(checker, \"EXPECTED_MANIFEST_LANE_KEY = \\\"helper-local\\\"\");",
    "try expectContains(checker, \"EXPECTED_MANIFEST_PHASE = \\\"Phase 7\\\"\");",
    "try expectContains(checker, \"EXPECTED_MANIFEST_ANCHOR = \\\"lib/string_helpers.c\\\"\");",
    "try expectContains(checker, \"EXPECTED_MANIFEST_STATE = \\\"expanded_starter_packet\\\"\");",
    "try expectContains(checker, \"try expectContains(helper, \\\\\\\\\"pub fn stringIsTerminated(\\\\\\\\\");\");",
    "try expectContains(checker, \"try expectContains(helper, \\\\\\\\\"pub fn string_is_terminated(\\\\\\\\\");\");",
    "try expectContains(checker, \"try expectContains(helper_tests, \\\\\\\\\"test \\\\\\\\\\\\\\\\\"phase 7 string helpers starter keeps termination checks bounded by the caller limit\\\\\\\\\\\\\\\\\" {\\\\\\\\\");\");",
    "try expectContains(checker, \"try expectContains(manifest, \\\\\\\\\"stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix\\\\\\\\\");\");",
    "try expectNotContains(helper, \"pub fn devmKasprintfStrarray\");",
    "try expectNotContains(helper, \"pub fn devm_kasprintf_strarray\");",
    "try expectNotContains(helper, \"pub fn parseIntArrayUser(\");",
    "try expectNotContains(helper, \"pub fn parse_int_array_user(\");",
    "try expectNotContains(helper_tests, \"devmKasprintfStrarray\");",
    "try expectNotContains(helper_tests, \"devm_kasprintf_strarray\");",
    "try expectNotContains(helper_tests, \"parseIntArrayUser\");",
    "try expectNotContains(helper_tests, \"parse_int_array_user\");",
    "try expectNotContains(manifest, \"\\\\\\\\\"devmKasprintfStrarray\\\\\\\\\"\");",
    "try expectNotContains(manifest, \"\\\\\\\\\"devm_kasprintf_strarray\\\\\\\\\"\");",
    "try expectNotContains(manifest, \"\\\\\\\\\"parseIntArrayUser\\\\\\\\\"\");",
    "try expectNotContains(manifest, \"\\\\\\\\\"parse_int_array_user\\\\\\\\\"\");",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_sample_boundary_zig = [_][]const u8{
    "phase 7 string helper boundary keeps the no-standalone-string-helper-sample policy lane-local",
    "* `*printf*`",
    "* `*vsprintf*`",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_format_boundary_zig = [_][]const u8{
    "test \"phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception\" {",
    "test \"phase 7 string helper format boundary stays on sample-boundary review surfaces only\" {",
    "* `*printf*`",
    "* `*vsprintf*`",
};

const REQUIRED_MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` still ships no standalone Phase 5 sample-root files here for:",
};

const EXPECTED_MANIFEST_OWNERSHIP_FOCUS = [_][]const u8{
    "TERMINATION_OWNERSHIP_MARKER",
    "CMDLINE_OWNERSHIP_MARKER",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_manifest_lane_key_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_manifest_lane_key_path);
    const text_expected_manifest_lane_key = try guard.readUtf8File(io, allocator, text_expected_manifest_lane_key_path);
    defer allocator.free(text_expected_manifest_lane_key);
    for (EXPECTED_MANIFEST_LANE_KEY) |marker| try guard.requireMarker(text_expected_manifest_lane_key, marker);
    const text_expected_manifest_anchor_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_manifest_anchor_path);
    const text_expected_manifest_anchor = try guard.readUtf8File(io, allocator, text_expected_manifest_anchor_path);
    defer allocator.free(text_expected_manifest_anchor);
    for (EXPECTED_MANIFEST_ANCHOR) |marker| try guard.requireMarker(text_expected_manifest_anchor, marker);
    const text_expected_manifest_state_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_manifest_state_path);
    const text_expected_manifest_state = try guard.readUtf8File(io, allocator, text_expected_manifest_state_path);
    defer allocator.free(text_expected_manifest_state);
    for (EXPECTED_MANIFEST_STATE) |marker| try guard.requireMarker(text_expected_manifest_state, marker);
    const text_expected_direct_repo_anchor_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_direct_repo_anchor_path);
    const text_expected_direct_repo_anchor = try guard.readUtf8File(io, allocator, text_expected_direct_repo_anchor_path);
    defer allocator.free(text_expected_direct_repo_anchor);
    for (EXPECTED_DIRECT_REPO_ANCHOR) |marker| try guard.requireMarker(text_expected_direct_repo_anchor, marker);
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_expected_covered_helpers_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_covered_helpers_path);
    const text_expected_covered_helpers = try guard.readUtf8File(io, allocator, text_expected_covered_helpers_path);
    defer allocator.free(text_expected_covered_helpers);
    for (EXPECTED_COVERED_HELPERS) |marker| try guard.requireMarker(text_expected_covered_helpers, marker);
    const text_devm_follow_on_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_devm_follow_on_marker_path);
    const text_devm_follow_on_marker = try guard.readUtf8File(io, allocator, text_devm_follow_on_marker_path);
    defer allocator.free(text_devm_follow_on_marker);
    for (DEVM_FOLLOW_ON_MARKER) |marker| try guard.requireMarker(text_devm_follow_on_marker, marker);
    const text_next_bounded_step_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_next_bounded_step_marker_path);
    const text_next_bounded_step_marker = try guard.readUtf8File(io, allocator, text_next_bounded_step_marker_path);
    defer allocator.free(text_next_bounded_step_marker);
    for (NEXT_BOUNDED_STEP_MARKER) |marker| try guard.requireMarker(text_next_bounded_step_marker, marker);
    const text_full_family_gap_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_full_family_gap_marker_path);
    const text_full_family_gap_marker = try guard.readUtf8File(io, allocator, text_full_family_gap_marker_path);
    defer allocator.free(text_full_family_gap_marker);
    for (FULL_FAMILY_GAP_MARKER) |marker| try guard.requireMarker(text_full_family_gap_marker, marker);
    const text_no_extra_sample_bullets_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_no_extra_sample_bullets_path);
    const text_no_extra_sample_bullets = try guard.readUtf8File(io, allocator, text_no_extra_sample_bullets_path);
    defer allocator.free(text_no_extra_sample_bullets);
    for (NO_EXTRA_SAMPLE_BULLETS) |marker| try guard.requireMarker(text_no_extra_sample_bullets, marker);
    const text_no_extra_sample_exclusions_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_no_extra_sample_exclusions_marker_path);
    const text_no_extra_sample_exclusions_marker = try guard.readUtf8File(io, allocator, text_no_extra_sample_exclusions_marker_path);
    defer allocator.free(text_no_extra_sample_exclusions_marker);
    for (NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER) |marker| try guard.requireMarker(text_no_extra_sample_exclusions_marker, marker);
    const text_format_boundary_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_format_boundary_marker_path);
    const text_format_boundary_marker = try guard.readUtf8File(io, allocator, text_format_boundary_marker_path);
    defer allocator.free(text_format_boundary_marker);
    for (FORMAT_BOUNDARY_MARKER) |marker| try guard.requireMarker(text_format_boundary_marker, marker);
    const text_format_boundary_focus_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_format_boundary_focus_path);
    const text_format_boundary_focus = try guard.readUtf8File(io, allocator, text_format_boundary_focus_path);
    defer allocator.free(text_format_boundary_focus);
    for (FORMAT_BOUNDARY_FOCUS) |marker| try guard.requireMarker(text_format_boundary_focus, marker);
    const text_cmdline_ownership_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_cmdline_ownership_marker_path);
    const text_cmdline_ownership_marker = try guard.readUtf8File(io, allocator, text_cmdline_ownership_marker_path);
    defer allocator.free(text_cmdline_ownership_marker);
    for (CMDLINE_OWNERSHIP_MARKER) |marker| try guard.requireMarker(text_cmdline_ownership_marker, marker);
    const text_termination_ownership_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_termination_ownership_marker_path);
    const text_termination_ownership_marker = try guard.readUtf8File(io, allocator, text_termination_ownership_marker_path);
    defer allocator.free(text_termination_ownership_marker);
    for (TERMINATION_OWNERSHIP_MARKER) |marker| try guard.requireMarker(text_termination_ownership_marker, marker);
    const text_expected_manifest_next_bounded_step_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_expected_manifest_next_bounded_step_path);
    const text_expected_manifest_next_bounded_step = try guard.readUtf8File(io, allocator, text_expected_manifest_next_bounded_step_path);
    defer allocator.free(text_expected_manifest_next_bounded_step);
    for (EXPECTED_MANIFEST_NEXT_BOUNDED_STEP) |marker| try guard.requireMarker(text_expected_manifest_next_bounded_step, marker);
    const text_manifest_lane_key_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_manifest_lane_key_marker_path);
    const text_manifest_lane_key_marker = try guard.readUtf8File(io, allocator, text_manifest_lane_key_marker_path);
    defer allocator.free(text_manifest_lane_key_marker);
    for (MANIFEST_LANE_KEY_MARKER) |marker| try guard.requireMarker(text_manifest_lane_key_marker, marker);
    const text_manifest_phase_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_manifest_phase_marker_path);
    const text_manifest_phase_marker = try guard.readUtf8File(io, allocator, text_manifest_phase_marker_path);
    defer allocator.free(text_manifest_phase_marker);
    for (MANIFEST_PHASE_MARKER) |marker| try guard.requireMarker(text_manifest_phase_marker, marker);
    const text_manifest_anchor_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_manifest_anchor_marker_path);
    const text_manifest_anchor_marker = try guard.readUtf8File(io, allocator, text_manifest_anchor_marker_path);
    defer allocator.free(text_manifest_anchor_marker);
    for (MANIFEST_ANCHOR_MARKER) |marker| try guard.requireMarker(text_manifest_anchor_marker, marker);
    const text_manifest_state_marker_path = try guard.joinPath(allocator, root, "lib/string_helpers.c");
    defer allocator.free(text_manifest_state_marker_path);
    const text_manifest_state_marker = try guard.readUtf8File(io, allocator, text_manifest_state_marker_path);
    defer allocator.free(text_manifest_state_marker);
    for (MANIFEST_STATE_MARKER) |marker| try guard.requireMarker(text_manifest_state_marker, marker);
    const text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-string-helpers-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-string-helpers-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md, marker);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_string_helpers_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-string-helpers-packet_py, marker);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_string_helpers_format_boundary_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py, marker);
    const text_required_markers__lib_string_helpers_zig_path = try guard.joinPath(allocator, root, "lib/string_helpers.zig");
    defer allocator.free(text_required_markers__lib_string_helpers_zig_path);
    const text_required_markers__lib_string_helpers_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_string_helpers_zig_path);
    defer allocator.free(text_required_markers__lib_string_helpers_zig);
    for (REQUIRED_MARKERS__lib_string_helpers_zig) |marker| try guard.requireMarker(text_required_markers__lib_string_helpers_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_sample_boundary_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_format_boundary.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_format_boundary_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig, marker);
    const text_required_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_required_markers__samples_zigux_readme_md_path);
    const text_required_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_required_markers__samples_zigux_readme_md);
    for (REQUIRED_MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__samples_zigux_readme_md, marker);
    const text_expected_manifest_ownership_focus_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_ownership_focus_path);
    const text_expected_manifest_ownership_focus = try guard.readUtf8File(io, allocator, text_expected_manifest_ownership_focus_path);
    defer allocator.free(text_expected_manifest_ownership_focus);
    for (EXPECTED_MANIFEST_OWNERSHIP_FOCUS) |marker| try guard.requireMarker(text_expected_manifest_ownership_focus, marker);
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
