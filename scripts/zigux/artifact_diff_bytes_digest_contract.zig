const std = @import("std");

const artifact_diff = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "bytes mode keeps sha256 helper and pass digest sentinel" {
    try expectContains(artifact_diff, "import hashlib");
    try expectContains(artifact_diff, "def sha256_hex(path: Path) -> str:");
    try expectContains(artifact_diff, "return hashlib.sha256(read_bytes(path)).hexdigest()");
    try expectContains(artifact_diff, "def compare_bytes(expected: Path, actual: Path)");
    try expectContains(artifact_diff, "if expected_digest == actual_digest:");
    try expectContains(artifact_diff, "extra_lines=[f\"SHA256={expected_digest}\"]");
    try expectContains(artifact_diff, "bytes_pass.extra_lines == [\"SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576\"]");
}

test "bytes drift reports expected and actual digests separately" {
    try expectContains(artifact_diff, "blob_a.write_bytes(b\"zigux-artifact-diff\")");
    try expectContains(artifact_diff, "blob_b.write_bytes(b\"zigux-artifact-DRIFT\")");
    try expectContains(artifact_diff, "f\"EXPECTED_SHA256={expected_digest}\"");
    try expectContains(artifact_diff, "f\"ACTUAL_SHA256={actual_digest}\"");
    try expectContains(artifact_diff, "\"EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576\",");
    try expectContains(artifact_diff, "\"ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94\",");
    try expectBefore(artifact_diff, "expected_digest = sha256_hex(expected)", "actual_digest = sha256_hex(actual)");
    try expectBefore(artifact_diff, "f\"EXPECTED_SHA256={expected_digest}\"", "f\"ACTUAL_SHA256={actual_digest}\"");
}

test "legacy sha256 alias stays normalized onto bytes output" {
    try expectContains(artifact_diff, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(artifact_diff, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(artifact_diff, "def normalize_mode(mode: str) -> str:");
    try expectContains(artifact_diff, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectContains(artifact_diff, "if mode == \"bytes\":");
    try expectContains(artifact_diff, "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])");
    try expectContains(artifact_diff, "assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try expectContains(artifact_diff, "\"bytes_pass\",");
    try expectContains(artifact_diff, "\"bytes_drift\",");
    try expectContains(artifact_diff, "\"legacy_sha256_alias\",");
    try expectBefore(artifact_diff, "\"bytes_drift\",", "\"legacy_sha256_alias\",");
}
