const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-phase1-parity.py");

const required_inputs = [_][]const u8{
    "ARTIFACT_DIFF_REL",
    "FIXTURE_REL",
    "MANIFEST_REL",
    "BLOCKERS_REL",
    "REPLAY_REL",
    "REPLAY_BUILD_REL",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

test "required-input roster names the six Phase 1 parity inputs" {
    try requireContains(checker_source, "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):");
    try requireContains(checker_source, "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")");
    try requireContains(checker_source, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try requireContains(checker_source, "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
    try requireContains(checker_source, "BLOCKERS_REL = Path(\"zigux/tests/fixtures/phase1_replay_blockers.json\")");
    try requireContains(checker_source, "REPLAY_REL = Path(\"zigux/tests/phase1_helpers.zig\")");
    try requireContains(checker_source, "REPLAY_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")");
    try requireContains(checker_source, "ensure((root / rel).exists(), f\"missing:{rel.as_posix()}\", issues)");
}

test "missing-input gate returns before artifact diff fixture and replay checks" {
    const missing_gate = "if issues:\n        return issues";
    try requireBefore(checker_source, "ensure((root / rel).exists(), f\"missing:{rel.as_posix()}\", issues)", missing_gate);
    try requireBefore(checker_source, missing_gate, "check_artifact_diff(root, issues)");
    try requireBefore(checker_source, missing_gate, "check_replay_routes(root, issues)");
    try requireBefore(checker_source, missing_gate, "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
}

test "public failure output preserves missing-input issue lines" {
    try requireContains(checker_source, "print(\"PHASE1_PARITY=fail\")");
    try requireContains(checker_source, "print(f\"PHASE1_PARITY_ISSUE={issue}\")");
    try requireBefore(checker_source, "issues = collect_issues(root)", "print(\"PHASE1_PARITY=fail\")");
    try requireBefore(checker_source, "print(f\"PHASE1_PARITY_ISSUE={issue}\")", "return 1");
}
