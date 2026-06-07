const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, marker) != null);
}

fn requireSingleMarker(marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, checker_source, marker));
}

test "parity checker runs artifact diff self-test before fixture comparisons" {
    try requireSingleMarker("def check_artifact_diff(root: Path, issues: list[str]) -> None:");
    try requireMarker("artifact_diff = root / ARTIFACT_DIFF_REL");
    try requireMarker("result = run_python(artifact_diff, \"--self-test\")");
    try requireMarker("ensure(result.returncode == 0, \"artifact_diff:self_test:returncode\", issues)");
    try requireMarker("ensure(\"ARTIFACT_DIFF_SELF_TEST=pass\" in result.stdout, \"artifact_diff:self_test:pass\", issues)");
    try requireMarker("ensure(\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23\" in result.stdout, \"artifact_diff:self_test:case_count\", issues)");
    try requireMarker("check_artifact_diff(root, issues)");
}

test "parity checker exercises text json bytes and legacy alias comparisons" {
    try requireMarker("(\"text\", [\"--mode\", \"text\", str(text_expected), str(text_actual)])");
    try requireMarker("(\"json\", [\"--mode\", \"json\", str(json_expected), str(json_actual)])");
    try requireMarker("(\"bytes\", [\"--mode\", \"bytes\", str(bytes_expected), str(bytes_actual)])");
    try requireMarker("(\"sha256\", [\"--mode\", \"sha256\", str(bytes_expected), str(bytes_actual)])");
    try requireMarker("for name, argv in cases:");
    try requireMarker("result = run_python(artifact_diff, *argv)");
    try requireMarker("ensure(result.returncode == 0, f\"artifact_diff:{name}:returncode\", issues)");
    try requireMarker("ensure(\"ARTIFACT_DIFF=pass\" in result.stdout, f\"artifact_diff:{name}:pass\", issues)");
}

test "artifact diff bridge builds deterministic sample artifacts" {
    try requireMarker("text_expected.write_text(\"alpha\\nbeta\\n\", encoding=\"utf-8\")");
    try requireMarker("text_actual.write_text(\"alpha\\nbeta\\n\", encoding=\"utf-8\")");
    try requireMarker("json_expected.write_text('{\"alpha\": 1, \"beta\": [2, 3]}\\n', encoding=\"utf-8\")");
    try requireMarker("json_actual.write_text('{\"beta\": [2, 3], \"alpha\": 1}\\n', encoding=\"utf-8\")");
    try requireMarker("bytes_expected.write_bytes(b\"zigux-parity\")");
    try requireMarker("bytes_actual.write_bytes(b\"zigux-parity\")");
    try requireMarker("with tempfile.TemporaryDirectory(prefix=\"phase1_parity_artifact_diff_\") as tmp_dir:");
}
