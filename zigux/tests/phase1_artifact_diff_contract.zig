const std = @import("std");

fn readSource(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    var last_error: anyerror = error.FileNotFound;
    for (paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            allocator,
            .limited(1024 * 1024),
        ) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    const paths = [_][]const u8{
        "scripts/zigux/artifact_diff.py",
        "../../scripts/zigux/artifact_diff.py",
    };
    return readSource(allocator, &paths);
}

fn readPhase1Parity(allocator: std.mem.Allocator) ![]u8 {
    const paths = [_][]const u8{
        "scripts/zigux/check-phase1-parity.py",
        "../../scripts/zigux/check-phase1-parity.py",
    };
    return readSource(allocator, &paths);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectMarkersInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{marker});
            return error.TestExpectedEqual;
        };
        cursor += relative + marker.len;
    }
}

test "artifact diff source pins Phase 1 comparison modes and parser aliases" {
    const artifact_diff_source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff_source);

    const markers = [_][]const u8{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "def normalize_mode(mode: str) -> str:",
        "return LEGACY_MODE_ALIASES.get(mode, mode)",
        "if mode in LEGACY_MODE_ALIASES:",
        "MODE={mode}",
    };
    for (markers) |marker| {
        try expectContains(artifact_diff_source, marker);
    }

    try expectAbsent(artifact_diff_source, "\"sha256\"),");
}

test "artifact diff self-test catalog keeps every Phase 1 gate case visible" {
    const artifact_diff_source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff_source);

    const cases = [_][]const u8{
        "\"text_pass\"",
        "\"text_mismatch\"",
        "\"json_pass\"",
        "\"json_mismatch\"",
        "\"json_invalid_expected\"",
        "\"json_invalid_actual\"",
        "\"json_invalid_both\"",
        "\"json_missing_expected\"",
        "\"json_missing_actual\"",
        "\"json_missing_both\"",
        "\"bytes_pass\"",
        "\"bytes_drift\"",
        "\"text_missing_expected\"",
        "\"text_missing_actual\"",
        "\"text_missing_both\"",
        "\"bytes_missing_expected\"",
        "\"bytes_missing_actual\"",
        "\"bytes_missing_both\"",
        "\"legacy_sha256_alias\"",
        "\"missing_mode_value_rejected\"",
        "\"missing_positional_arguments_rejected\"",
        "\"invalid_mode_rejected\"",
        "\"extra_positional_rejected\"",
    };

    try expectMarkersInOrder(artifact_diff_source, &cases);
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST=pass");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)");
}

test "artifact diff outputs distinguish stable pass and drift signals" {
    const artifact_diff_source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff_source);

    const markers = [_][]const u8{
        "ARTIFACT_DIFF={status}",
        "EXPECTED_EXISTS={expected_exists}",
        "ACTUAL_EXISTS={actual_exists}",
        "EXPECTED_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}",
        "ACTUAL_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}",
        "EXPECTED_UTF8_ERROR={path}:{exc.start}: {exc.reason}",
        "ACTUAL_UTF8_ERROR={path}:{exc.start}: {exc.reason}",
        "SHA256={expected_digest}",
        "EXPECTED_SHA256={expected_digest}",
        "ACTUAL_SHA256={actual_digest}",
    };
    for (markers) |marker| {
        try expectContains(artifact_diff_source, marker);
    }

    try expectOnce(artifact_diff_source, "def compare_text(expected: Path, actual: Path) -> ComparisonResult:");
    try expectOnce(artifact_diff_source, "def compare_json(expected: Path, actual: Path) -> ComparisonResult:");
    try expectOnce(artifact_diff_source, "def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:");
}

test "phase1 parity checker keeps artifact diff gate wired into fixture validation" {
    const phase1_parity_source = try readPhase1Parity(std.testing.allocator);
    defer std.testing.allocator.free(phase1_parity_source);

    const markers = [_][]const u8{
        "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")",
        "def check_artifact_diff(root: Path, issues: list[str]) -> None:",
        "run_python(artifact_diff, \"--self-test\")",
        "ARTIFACT_DIFF_SELF_TEST=pass",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23",
        "(\"text\", [\"--mode\", \"text\", str(text_expected), str(text_actual)]),",
        "(\"json\", [\"--mode\", \"json\", str(json_expected), str(json_actual)]),",
        "(\"bytes\", [\"--mode\", \"bytes\", str(bytes_expected), str(bytes_actual)]),",
        "(\"sha256\", [\"--mode\", \"sha256\", str(bytes_expected), str(bytes_actual)]),",
        "artifact_diff:{name}:returncode",
        "artifact_diff:{name}:pass",
    };
    for (markers) |marker| {
        try expectContains(phase1_parity_source, marker);
    }
}
