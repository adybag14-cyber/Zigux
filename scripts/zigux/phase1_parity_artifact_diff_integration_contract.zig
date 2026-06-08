const std = @import("std");
const testing = std.testing;

const parity_source = @embedFile("check-phase1-parity.py");

fn hasLiveArtifactDiffIntegration() bool {
    return std.mem.indexOf(u8, parity_source, "def check_artifact_diff(root: Path, issues: list[str]) -> None:") != null and
        std.mem.indexOf(u8, parity_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23") != null;
}

fn requireLiveArtifactDiffIntegration() !void {
    if (!hasLiveArtifactDiffIntegration()) return error.SkipZigTest;
}

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, parity_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, parity_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, parity_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn expectCount(needle: []const u8, expected: usize) !void {
    var remaining: []const u8 = parity_source;
    var actual: usize = 0;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        actual += 1;
        remaining = remaining[index + needle.len ..];
    }
    try testing.expectEqual(expected, actual);
}

test "parity checker runs artifact diff self-test before fixture checks" {
    try requireLiveArtifactDiffIntegration();

    try expectContains("def check_artifact_diff(root: Path, issues: list[str]) -> None:");
    try expectContains("artifact_diff = root / ARTIFACT_DIFF_REL");
    try expectContains("result = run_python(artifact_diff, \"--self-test\")");
    try expectContains("ensure(result.returncode == 0, \"artifact_diff:self_test:returncode\", issues)");
    try expectContains("ensure(\"ARTIFACT_DIFF_SELF_TEST=pass\" in result.stdout, \"artifact_diff:self_test:pass\", issues)");
    try expectContains("ensure(\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23\" in result.stdout, \"artifact_diff:self_test:case_count\", issues)");
    try expectBefore("check_artifact_diff(root, issues)", "check_replay_routes(root, issues)");
    try expectBefore("check_artifact_diff(root, issues)", "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
}

test "parity checker exercises text json bytes and legacy alias pass modes" {
    try requireLiveArtifactDiffIntegration();

    try expectContains("text_expected.write_text(\"alpha\\nbeta\\n\", encoding=\"utf-8\")");
    try expectContains("json_expected.write_text('{\"alpha\": 1, \"beta\": [2, 3]}\\n', encoding=\"utf-8\")");
    try expectContains("bytes_expected.write_bytes(b\"zigux-parity\")");
    try expectContains("bytes_actual.write_bytes(b\"zigux-parity\")");
    try expectContains("(\"text\", [\"--mode\", \"text\", str(text_expected), str(text_actual)]),");
    try expectContains("(\"json\", [\"--mode\", \"json\", str(json_expected), str(json_actual)]),");
    try expectContains("(\"bytes\", [\"--mode\", \"bytes\", str(bytes_expected), str(bytes_actual)]),");
    try expectContains("(\"sha256\", [\"--mode\", \"sha256\", str(bytes_expected), str(bytes_actual)]),");
    try expectCount("run_python(artifact_diff,", 2);
}

test "parity checker reports per-mode artifact diff integration failures" {
    try requireLiveArtifactDiffIntegration();

    try expectContains("for name, argv in cases:");
    try expectContains("ensure(result.returncode == 0, f\"artifact_diff:{name}:returncode\", issues)");
    try expectContains("ensure(\"ARTIFACT_DIFF=pass\" in result.stdout, f\"artifact_diff:{name}:pass\", issues)");
    try expectBefore("cases = (", "for name, argv in cases:");
    try expectBefore("for name, argv in cases:", "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
}
