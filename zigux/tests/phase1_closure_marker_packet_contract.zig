const std = @import("std");

const validator_path = "scripts/zigux/validate-phase1-closure.py";

fn readValidatorSource() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        validator_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase1 closure validator keeps marker packet sources explicit" {
    const validator_source = try readValidatorSource();
    defer std.testing.allocator.free(validator_source);

    try expectContains(validator_source, "EXPECTED_CLOSURE_MARKERS = {");
    try expectContains(validator_source, "\"status\": \"`PHASE1_STATUS=parked`\"");
    try expectContains(validator_source, "\"helper_count\": \"`PHASE1_HELPER_COUNT=13`\"");
    try expectContains(validator_source, "\"closure_validator\": \"`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`\"");
    try expectContains(validator_source, "\"route_summary_guard\": \"`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\"");
    try expectContains(validator_source, "\"shared_tests_route\": \"`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\"");
    try expectContains(validator_source, "\"direct_anchor_manifest_gate\": \"`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    try expectContains(validator_source, "\"next_step\": \"`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");
}

test "phase1 closure validator rejects stale closure and makefile markers" {
    const validator_source = try readValidatorSource();
    defer std.testing.allocator.free(validator_source);

    try expectContains(validator_source, "FORBIDDEN_CLOSURE_MARKERS = {");
    try expectContains(validator_source, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectContains(validator_source, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
    try expectContains(validator_source, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectContains(validator_source, "\"phase1-validate:\"");
    try expectContains(validator_source, "\"phase1-test:\"");
    try expectContains(validator_source, "\"phase1-bench:\"");
    try expectContains(validator_source, "\"phase1:\"");
    try expectContains(validator_source, "forbidden_marker:actual_count=");
}

test "phase1 closure validator ties manifest review anchors to helper families" {
    const validator_source = try readValidatorSource();
    defer std.testing.allocator.free(validator_source);

    try expectContains(validator_source, "EXPECTED_BITMAP_REVIEW_ANCHORS = {");
    try expectContains(validator_source, "EXPECTED_FIND_BIT_REVIEW_ANCHORS = {");
    try expectContains(validator_source, "EXPECTED_RBTREE_REVIEW_ANCHORS = {");
    try expectContains(validator_source, "EXPECTED_STRING_REVIEW_ANCHORS = {");
    try expectContains(validator_source, "require_expected_mapping(f\"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig\"");
    try expectContains(validator_source, "require_expected_mapping(f\"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig\"");
    try expectContains(validator_source, "require_expected_mapping(f\"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/rbtree.zig\"");
    try expectContains(validator_source, "require_expected_mapping(f\"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/string.zig\"");
    try expectContains(validator_source, "\"andnot_scan_entrypoint_contract\"");
    try expectContains(validator_source, "\"cached_root_alias_anchor\"");
    try expectContains(validator_source, "\"linux_alias_anchor\"");
    try expectContains(validator_source, "\"strnchr_review_summary\"");
}

test "phase1 closure validator self-test covers marker drift and delegated checkers" {
    const validator_source = try readValidatorSource();
    defer std.testing.allocator.free(validator_source);

    try expectContains(validator_source, "DELEGATED_CHECKERS = (");
    try expectContains(validator_source, "for script_rel, label in DELEGATED_CHECKERS:");
    try expectContains(validator_source, "delegated:{label}:");
    try expectContains(validator_source, "(\"missing_restore_state\"");
    try expectContains(validator_source, "(\"old_next_step_marker\"");
    try expectContains(validator_source, "(\"forbidden_old_marker\"");
    try expectContains(validator_source, "(\"missing_find_bit_review_guard\"");
    try expectContains(validator_source, "(\"stale_rbtree_review_guard\"");
    try expectContains(validator_source, "(\"stale_direct_anchor_manifest_gate_marker\"");
    try expectContains(validator_source, "(\"duplicate_manifest_lane_rule_summary\"");
    try expectContains(validator_source, "(\"failing_direct_anchor_manifest_gate_checker\"");
    try expectContains(validator_source, "PHASE1_CLOSURE_SELF_TEST_CASE_COUNT=");

    try expectInOrder(
        validator_source,
        "failures = [f\"missing_file:{path.as_posix()}\"",
        "for label, marker in EXPECTED_CLOSURE_MARKERS.items():",
    );
    try expectInOrder(
        validator_source,
        "for label, marker in EXPECTED_CLOSURE_MARKERS.items():",
        "for script_rel, label in DELEGATED_CHECKERS:",
    );
}
