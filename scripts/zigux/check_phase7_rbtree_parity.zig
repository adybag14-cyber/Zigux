const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RBTREE_PARITY=pass";
pub const self_test_pass_marker = "PHASE7_RBTREE_PARITY_SELF_TEST=pass";

const EXPECTED_MANIFEST_ANCHOR = [_][]const u8{
    "lib/rbtree.c",
};

const EXPECTED_MANIFEST_STATE = [_][]const u8{
    "direct_helper_slice_checker_test_note_survey_manifest_fixture_harness",
};

const EXPECTED_MANIFEST_READABLE_MAKEFILE_MARKERS = [_][]const u8{
    "phase7-validate:",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
};

const EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = [_][]const u8{
    "Stay in the same `kernel-leaf-libraries` lane and keep `zigux/tests/fixtures/phase7_rbtree.json` plus `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity companions, including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases, while keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers aligned with `zigux/tests/phase7_build.zig` so helper path, shared `phase7-validate` route, still-absent `phase7-test:` and `phase7:` markers, and legacy companion framing stay aligned while keeping the cached-churn invariants witness aligned with the dedicated replay and without widening beyond the rbtree packet.",
};

const NEXT_STEP_WRAPPER_MARKER = [_][]const u8{
    "while keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers aligned with `zigux/tests/phase7_build.zig`",
};

const NEXT_STEP_ERASE_CASES_MARKER = [_][]const u8{
    "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases",
};

const DIRECT_BUILD_READBACK_MARKER = [_][]const u8{
    "`zigux/tests/phase7_build.zig` now rematerialized through the same authenticated reread path in this slot, so keep it explicit as returned shared non-owner build evidence without treating it as helper-local ownership.",
};

const SLICE_AUTHENTICATED_BUILD_MARKER = [_][]const u8{
    "public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field in `zigux/tests/phase7_rbtree_manifest.json`, because `zigux/tests/phase7_build.zig` and the other listed legacy or shared non-owner surfaces all rematerialized through authenticated rereads in this slot",
};

const SLICE_ERASE_BOUNDARY_MARKER = [_][]const u8{
    "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases",
};

const DIRECT_ERASE_SCENARIOS_MARKER = [_][]const u8{
    "non-leftmost cached erase, singleton cached erase, and plain erase-init reseed scenarios",
};

const MANIFEST_BUILD_PROVENANCE_MARKER = [_][]const u8{
    "build-surface provenance must stay explicit: in this runtime `zigux/tests/phase7_build.zig`, `tools/lib/rbtree.zig`, `scripts\\zigux/check_phase7_build_wiring.zig`, `scripts\\zigux/validate_phase7.zig`, `zigux/Makefile`, and the helper-local rbtree packet all rematerialized through authenticated rereads, so shared non-owner build evidence stays reviewable without public-fallback caveats on current master",
};

const MANIFEST_EMPTY_FALLBACK_MARKER = [_][]const u8{
    "machine-readable fallback provenance should stay empty in this packet while the readable non-owner surfaces all rematerialize through authenticated rereads in this runtime",
};

const MANIFEST_ERASE_BOUNDARY_MARKER = [_][]const u8{
    "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay",
};

const MAKEFILE_POSITIVE_ROUTE_MARKER = [_][]const u8{
    "positive shared build-route truthfulness must stay explicit too: `zigux/Makefile` now returns shared `phase7-validate` plus dedicated `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, while `phase7-test:` and `phase7:` stay listed under `absent_makefile_markers` until broader shared-control routes really materialize",
};

const DIRECT_WRAPPER_ROUTE_MARKER = [_][]const u8{
    "`zigux/Makefile` now returns shared `phase7-validate` plus dedicated `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrapper markers",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-rbtree-slice_md = [_][]const u8{
    "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_fixture_harness_anchor`",
    "`PHASE7_LANE_KEY=P7-L13`",
    "`lib/rbtree.zig`",
    "`tools/lib/rbtree.zig`",
    "`zigux/tests/fixtures/phase7_rbtree.json`",
    "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
    "helper-local implementation now remains rooted at `lib/rbtree.zig`",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-rbtree-direct-anchor-note_md = [_][]const u8{
    "`zigux/tests/fixtures/phase7_rbtree.json`",
    "Fresh authenticated GitHub reread in this slot directly returned:",
    "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
    "Fresh current-master reread in this slot also directly returned these shared, legacy, or roadmap-adjacent non-owner surfaces:",
    "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-rbtree-parity_py = [_][]const u8{
    "import json",
    "EXPECTED_MANIFEST_LANE_KEY = \"P7-L13\"",
    "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
    "EXPECTED_MANIFEST_ANCHOR = \"lib/rbtree.c\"",
    "EXPECTED_MANIFEST_STATE = \"direct_helper_slice_checker_test_note_survey_manifest_fixture_harness\"",
    "PHASE7_RBTREE_PARITY=pass",
    "PHASE7_RBTREE_PARITY=fail",
    "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
    "MISSING_PHASE7_RBTREE_FILES_START",
    "MISSING_PHASE7_RBTREE_FILES_END",
    "MISSING_PHASE7_RBTREE_MARKERS_START",
    "MISSING_PHASE7_RBTREE_MARKERS_END",
    "\"zigux/tests/fixtures/phase7_rbtree.json\": [",
    "\"zigux/tests/fixtures/phase7_rbtree_c_harness.c\": [",
    "NEXT_STEP_WRAPPER_MARKER = (",
    "NEXT_STEP_ERASE_CASES_MARKER = (",
    "DIRECT_BUILD_READBACK_MARKER = (",
    "SLICE_AUTHENTICATED_BUILD_MARKER = (",
    "SLICE_ERASE_BOUNDARY_MARKER = (",
    "DIRECT_ERASE_SCENARIOS_MARKER = (",
    "MANIFEST_BUILD_PROVENANCE_MARKER = (",
    "MANIFEST_EMPTY_FALLBACK_MARKER = (",
    "MANIFEST_ERASE_BOUNDARY_MARKER = (",
    "MAKEFILE_POSITIVE_ROUTE_MARKER = (",
    "DIRECT_WRAPPER_ROUTE_MARKER = (",
    "assert cases_run == SELF_TEST_CASE_COUNT",
};

const REQUIRED_MARKERS__lib_rbtree_zig = [_][]const u8{
    "pub const Node = struct {",
    "pub const RootCached = struct {",
    "pub fn rb_find_add_cached",
    "pub fn eraseInit(node: *Node, root: *Root) void {",
    "pub fn rb_next_postorder",
};

const REQUIRED_MARKERS__zigux_tests_phase7_rbtree_zig = [_][]const u8{
    "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers",
    "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries",
    "phase 7 rbtree companion replays non-leftmost cached erase ownership boundaries",
    "phase 7 rbtree companion replays singleton cached erase ownership until clearNode",
    "phase 7 rbtree companion replays plain erase-init ownership boundaries",
    "phase 7 rbtree companion replays reverse traversal aliases and detached null stops",
};

const REQUIRED_MARKERS__zigux_tests_phase7_rbtree_survey_zig = [_][]const u8{
    "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful",
    "try expectSliceContains(manifest.visible_paths, \"zigux/tests/fixtures/phase7_rbtree.json\");",
    "try expectSliceContains(manifest.visible_paths, \"zigux/tests/fixtures/phase7_rbtree_c_harness.c\");",
    "try expectSliceContains(manifest.readable_non_owner_paths, \"zigux/tests/phase7_build.zig\");",
    "try expectSliceContains(manifest.readable_makefile_markers, \"phase7-rbtree-test:\");",
    "try expectSliceContains(manifest.readable_makefile_markers, \"phase7-rbtree-survey:\");",
    "try std.testing.expectEqual(@as(usize, 0), manifest.public_fallback_non_owner_paths.len);",
    "try expectSliceContains(manifest.ownership_focus, \"fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay\");",
    "try expectContains(manifest.next_bounded_step, \"including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases\");",
    "try expectContains(manifest.next_bounded_step, \"zigux/tests/fixtures/phase7_rbtree_c_harness.c\");",
    "try expectContains(manifest.next_bounded_step, \"phase7-rbtree-test:\");",
    "try expectContains(manifest.next_bounded_step, \"phase7-rbtree-survey:\");",
    "try expectContains(manifest.next_bounded_step, \"phase7-test:\");",
    "try expectContains(makefile, \"phase7-validate:\");",
    "try expectContains(makefile, \"phase7-rbtree-test:\");",
    "try expectContains(makefile, \"phase7-rbtree-survey:\");",
    "try expectContains(slice_note, \"public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field\");",
    "try expectContains(fixture, \"\\\"packet\\\": \\\"phase7-rbtree-parity-fixture\\\"\");",
    "try expectContains(c_harness, \"ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness\");",
};

const REQUIRED_MARKERS__zigux_tests_phase7_rbtree_manifest_json = [_][]const u8{
    "\"current_direct_readback_state\": \"direct_helper_slice_checker_test_note_survey_manifest_fixture_harness\"",
    "\"public_fallback_non_owner_paths\": []",
    "\"phase7-rbtree-test:\"",
    "\"phase7-rbtree-survey:\"",
    "\"zigux/tests/fixtures/phase7_rbtree.json\"",
    "\"zigux/tests/fixtures/phase7_rbtree_c_harness.c\"",
    "fixture truthfulness must keep `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity evidence",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase7_rbtree_json = [_][]const u8{
    "\"packet\": \"phase7-rbtree-parity-fixture\"",
    "\"ordered_duplicate_range\"",
    "\"cached_leftmost_promotion\"",
    "\"non_leftmost_cached_erase\"",
    "\"singleton_cached_erase\"",
    "\"plain_erase_init_reseed\"",
    "\"postorder_null_stop\"",
    "\"reverse_alias_detached\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase7_rbtree_c_harness_c = [_][]const u8{
    "struct phase7_rbtree_c_harness {",
    ".packet = \"phase7-rbtree-parity-fixture\",",
    ".current_master_state = \"ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness\",",
    ".ordered_duplicate_range = {",
    ".non_leftmost_cached_erase = {",
    ".singleton_cached_erase = {",
    ".plain_erase_init_reseed = {",
    ".reverse_alias_detached = {",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase7-validate:",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_manifest_anchor_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_expected_manifest_anchor_path);
    const text_expected_manifest_anchor = try guard.readUtf8File(io, allocator, text_expected_manifest_anchor_path);
    defer allocator.free(text_expected_manifest_anchor);
    for (EXPECTED_MANIFEST_ANCHOR) |marker| try guard.requireMarker(text_expected_manifest_anchor, marker);
    const text_expected_manifest_state_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_expected_manifest_state_path);
    const text_expected_manifest_state = try guard.readUtf8File(io, allocator, text_expected_manifest_state_path);
    defer allocator.free(text_expected_manifest_state);
    for (EXPECTED_MANIFEST_STATE) |marker| try guard.requireMarker(text_expected_manifest_state, marker);
    const text_expected_manifest_readable_makefile_markers_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_expected_manifest_readable_makefile_markers_path);
    const text_expected_manifest_readable_makefile_markers = try guard.readUtf8File(io, allocator, text_expected_manifest_readable_makefile_markers_path);
    defer allocator.free(text_expected_manifest_readable_makefile_markers);
    for (EXPECTED_MANIFEST_READABLE_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_expected_manifest_readable_makefile_markers, marker);
    const text_expected_manifest_next_bounded_step_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_expected_manifest_next_bounded_step_path);
    const text_expected_manifest_next_bounded_step = try guard.readUtf8File(io, allocator, text_expected_manifest_next_bounded_step_path);
    defer allocator.free(text_expected_manifest_next_bounded_step);
    for (EXPECTED_MANIFEST_NEXT_BOUNDED_STEP) |marker| try guard.requireMarker(text_expected_manifest_next_bounded_step, marker);
    const text_next_step_wrapper_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_next_step_wrapper_marker_path);
    const text_next_step_wrapper_marker = try guard.readUtf8File(io, allocator, text_next_step_wrapper_marker_path);
    defer allocator.free(text_next_step_wrapper_marker);
    for (NEXT_STEP_WRAPPER_MARKER) |marker| try guard.requireMarker(text_next_step_wrapper_marker, marker);
    const text_next_step_erase_cases_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_next_step_erase_cases_marker_path);
    const text_next_step_erase_cases_marker = try guard.readUtf8File(io, allocator, text_next_step_erase_cases_marker_path);
    defer allocator.free(text_next_step_erase_cases_marker);
    for (NEXT_STEP_ERASE_CASES_MARKER) |marker| try guard.requireMarker(text_next_step_erase_cases_marker, marker);
    const text_direct_build_readback_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_direct_build_readback_marker_path);
    const text_direct_build_readback_marker = try guard.readUtf8File(io, allocator, text_direct_build_readback_marker_path);
    defer allocator.free(text_direct_build_readback_marker);
    for (DIRECT_BUILD_READBACK_MARKER) |marker| try guard.requireMarker(text_direct_build_readback_marker, marker);
    const text_slice_authenticated_build_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_slice_authenticated_build_marker_path);
    const text_slice_authenticated_build_marker = try guard.readUtf8File(io, allocator, text_slice_authenticated_build_marker_path);
    defer allocator.free(text_slice_authenticated_build_marker);
    for (SLICE_AUTHENTICATED_BUILD_MARKER) |marker| try guard.requireMarker(text_slice_authenticated_build_marker, marker);
    const text_slice_erase_boundary_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_slice_erase_boundary_marker_path);
    const text_slice_erase_boundary_marker = try guard.readUtf8File(io, allocator, text_slice_erase_boundary_marker_path);
    defer allocator.free(text_slice_erase_boundary_marker);
    for (SLICE_ERASE_BOUNDARY_MARKER) |marker| try guard.requireMarker(text_slice_erase_boundary_marker, marker);
    const text_direct_erase_scenarios_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_direct_erase_scenarios_marker_path);
    const text_direct_erase_scenarios_marker = try guard.readUtf8File(io, allocator, text_direct_erase_scenarios_marker_path);
    defer allocator.free(text_direct_erase_scenarios_marker);
    for (DIRECT_ERASE_SCENARIOS_MARKER) |marker| try guard.requireMarker(text_direct_erase_scenarios_marker, marker);
    const text_manifest_build_provenance_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_manifest_build_provenance_marker_path);
    const text_manifest_build_provenance_marker = try guard.readUtf8File(io, allocator, text_manifest_build_provenance_marker_path);
    defer allocator.free(text_manifest_build_provenance_marker);
    for (MANIFEST_BUILD_PROVENANCE_MARKER) |marker| try guard.requireMarker(text_manifest_build_provenance_marker, marker);
    const text_manifest_empty_fallback_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_manifest_empty_fallback_marker_path);
    const text_manifest_empty_fallback_marker = try guard.readUtf8File(io, allocator, text_manifest_empty_fallback_marker_path);
    defer allocator.free(text_manifest_empty_fallback_marker);
    for (MANIFEST_EMPTY_FALLBACK_MARKER) |marker| try guard.requireMarker(text_manifest_empty_fallback_marker, marker);
    const text_manifest_erase_boundary_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_manifest_erase_boundary_marker_path);
    const text_manifest_erase_boundary_marker = try guard.readUtf8File(io, allocator, text_manifest_erase_boundary_marker_path);
    defer allocator.free(text_manifest_erase_boundary_marker);
    for (MANIFEST_ERASE_BOUNDARY_MARKER) |marker| try guard.requireMarker(text_manifest_erase_boundary_marker, marker);
    const text_makefile_positive_route_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_makefile_positive_route_marker_path);
    const text_makefile_positive_route_marker = try guard.readUtf8File(io, allocator, text_makefile_positive_route_marker_path);
    defer allocator.free(text_makefile_positive_route_marker);
    for (MAKEFILE_POSITIVE_ROUTE_MARKER) |marker| try guard.requireMarker(text_makefile_positive_route_marker, marker);
    const text_direct_wrapper_route_marker_path = try guard.joinPath(allocator, root, "lib/rbtree.c");
    defer allocator.free(text_direct_wrapper_route_marker_path);
    const text_direct_wrapper_route_marker = try guard.readUtf8File(io, allocator, text_direct_wrapper_route_marker_path);
    defer allocator.free(text_direct_wrapper_route_marker);
    for (DIRECT_WRAPPER_ROUTE_MARKER) |marker| try guard.requireMarker(text_direct_wrapper_route_marker, marker);
    const text_required_markers__documentation_zigux_phase7-rbtree-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-rbtree-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-rbtree-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-rbtree-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-rbtree-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-rbtree-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-rbtree-slice_md, marker);
    const text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md_path);
    const text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-rbtree-direct-anchor-note_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-rbtree-direct-anchor-note_md, marker);
    const text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_rbtree_parity.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py_path);
    const text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-rbtree-parity_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-rbtree-parity_py, marker);
    const text_required_markers__lib_rbtree_zig_path = try guard.joinPath(allocator, root, "lib/rbtree.zig");
    defer allocator.free(text_required_markers__lib_rbtree_zig_path);
    const text_required_markers__lib_rbtree_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_rbtree_zig_path);
    defer allocator.free(text_required_markers__lib_rbtree_zig);
    for (REQUIRED_MARKERS__lib_rbtree_zig) |marker| try guard.requireMarker(text_required_markers__lib_rbtree_zig, marker);
    const text_required_markers__zigux_tests_phase7_rbtree_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_zig_path);
    const text_required_markers__zigux_tests_phase7_rbtree_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_rbtree_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_rbtree_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_rbtree_zig, marker);
    const text_required_markers__zigux_tests_phase7_rbtree_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_rbtree_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_rbtree_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_rbtree_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_rbtree_survey_zig, marker);
    const text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_rbtree_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_rbtree_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_rbtree_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_rbtree_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_rbtree_manifest_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase7_rbtree_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_rbtree_json_path);
    const text_required_markers__zigux_tests_fixtures_phase7_rbtree_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase7_rbtree_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_rbtree_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase7_rbtree_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase7_rbtree_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase7_rbtree_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase7_rbtree_c_harness_c, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
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
