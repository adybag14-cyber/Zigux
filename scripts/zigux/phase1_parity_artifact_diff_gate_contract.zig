const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");
const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn artifactDiffUsesCurrentBytesMode() bool {
    return std.mem.indexOf(u8, artifact_diff_source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}") != null;
}

fn parityCheckerUsesCurrentManifestGate() bool {
    return std.mem.indexOf(u8, checker_source, "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")") != null;
}

test "phase1 parity checker keeps artifact-diff gate inputs explicit" {
    try expectContains(checker_source, "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")");
    try expectContains(checker_source, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try expectContains(checker_source, "HARNESS_REL = Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")");

    if (parityCheckerUsesCurrentManifestGate()) {
        try expectContains(checker_source, "run_python(artifact_diff, \"--self-test\")");
        try expectContains(checker_source, "ARTIFACT_DIFF_SELF_TEST=pass");
        try expectContains(checker_source, "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
        try expectContains(checker_source, "BLOCKERS_REL = Path(\"zigux/tests/fixtures/phase1_replay_blockers.json\")");
        try expectContains(checker_source, "REPLAY_REL = Path(\"zigux/tests/phase1_helpers.zig\")");
        try expectContains(checker_source, "REPLAY_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")");
        try expectContains(checker_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23");
        try expectContains(checker_source, "(\"sha256\", [\"--mode\", \"sha256\", str(bytes_expected), str(bytes_actual)])");
        try expectContains(checker_source, "PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT=");
        try expectContains(checker_source, "EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS");
        try expectBefore(
            checker_source,
            "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):",
            "check_artifact_diff(root, issues)",
        );
    } else {
        try expectContains(checker_source, "required_paths = [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL]");
    }
}

test "artifact diff gate preserves deterministic modes and diagnostics" {
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF=pass");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF=fail");
    try expectContains(artifact_diff_source, "EXPECTED_EXISTS=");
    try expectContains(artifact_diff_source, "ACTUAL_EXISTS=");
    try expectContains(artifact_diff_source, "EXPECTED_SHA256=");
    try expectContains(artifact_diff_source, "ACTUAL_SHA256=");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");

    if (artifactDiffUsesCurrentBytesMode()) {
        try expectContains(artifact_diff_source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
        try expectContains(artifact_diff_source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
        try expectContains(artifact_diff_source, "SELF_TEST_CASES = [");
        try expectContains(artifact_diff_source, "\"bytes_pass\"");
        try expectContains(artifact_diff_source, "\"bytes_drift\"");
        try expectContains(artifact_diff_source, "\"legacy_sha256_alias\"");
        try expectContains(artifact_diff_source, "\"missing_mode_value_rejected\"");
        try expectContains(artifact_diff_source, "\"extra_positional_rejected\"");
        try expectContains(artifact_diff_source, "path_problem_lines(expected: Path, actual: Path)");
        try expectContains(artifact_diff_source, "EXPECTED_IS_FILE=");
        try expectContains(artifact_diff_source, "ACTUAL_IS_FILE=");
        try expectBefore(artifact_diff_source, "MODE_CHOICES", "LEGACY_MODE_ALIASES");
    } else {
        try expectContains(artifact_diff_source, "parser.add_argument('--mode', choices=['text', 'json', 'sha256'])");
        try expectContains(artifact_diff_source, "'sha256_pass'");
        try expectContains(artifact_diff_source, "'sha256_drift'");
        try expectContains(artifact_diff_source, "'invalid_mode_rejected'");
    }
}
