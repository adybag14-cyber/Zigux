const std = @import("std");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    WrongMarkerOrder,
};

const parity_checker_path = "scripts/zigux/check-phase1-parity.py";
const artifact_diff_path = "scripts/zigux/artifact_diff.py";

const checker_path_markers = [_][]const u8{
    "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")",
    "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):",
};

const checker_artifact_gate_markers = [_][]const u8{
    "def check_artifact_diff(root: Path, issues: list[str]) -> None:",
    "result = run_python(artifact_diff, \"--self-test\")",
    "ensure(result.returncode == 0, \"artifact_diff:self_test:returncode\", issues)",
    "ensure(\"ARTIFACT_DIFF_SELF_TEST=pass\" in result.stdout, \"artifact_diff:self_test:pass\", issues)",
    "ensure(\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23\" in result.stdout, \"artifact_diff:self_test:case_count\", issues)",
};

const checker_mode_probe_markers = [_][]const u8{
    "(\"text\", [\"--mode\", \"text\", str(text_expected), str(text_actual)]),",
    "(\"json\", [\"--mode\", \"json\", str(json_expected), str(json_actual)]),",
    "(\"bytes\", [\"--mode\", \"bytes\", str(bytes_expected), str(bytes_actual)]),",
    "(\"sha256\", [\"--mode\", \"sha256\", str(bytes_expected), str(bytes_actual)]),",
    "ensure(result.returncode == 0, f\"artifact_diff:{name}:returncode\", issues)",
    "ensure(\"ARTIFACT_DIFF=pass\" in result.stdout, f\"artifact_diff:{name}:pass\", issues)",
};

const checker_collect_order_markers = [_][]const u8{
    "check_artifact_diff(root, issues)",
    "check_replay_routes(root, issues)",
    "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)",
};

const artifact_diff_public_markers = [_][]const u8{
    "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
    "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
    "\"legacy_sha256_alias\",",
    "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requirePresent(haystack: []const u8, needle: []const u8) !void {
    _ = std.mem.indexOf(u8, haystack, needle) orelse return ContractError.MissingMarker;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return ContractError.MissingMarker;
    if (std.mem.indexOf(u8, haystack[first + needle.len ..], needle) != null) {
        return ContractError.DuplicateMarker;
    }
}

fn requireAllPresent(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requirePresent(haystack, marker);
    }
}

fn requireAllOnce(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requireOnce(haystack, marker);
    }
}

fn requireInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return ContractError.MissingMarker;
        cursor += relative + marker.len;
    }
}

fn functionBlock(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, start_marker) orelse return ContractError.MissingMarker;
    const relative_end = std.mem.indexOf(u8, source[start..], end_marker) orelse return ContractError.MissingMarker;
    return source[start .. start + relative_end];
}

test "phase1 parity checker keeps artifact diff as a required gate input" {
    const checker = try readRepoFile(std.testing.allocator, parity_checker_path);
    defer std.testing.allocator.free(checker);

    try requireAllPresent(checker, &checker_path_markers);
}

test "phase1 parity checker runs artifact diff self-test before fixture checks" {
    const checker = try readRepoFile(std.testing.allocator, parity_checker_path);
    defer std.testing.allocator.free(checker);

    const gate = try functionBlock(checker, checker_artifact_gate_markers[0], "\n\ndef check_replay_routes");
    try requireAllPresent(gate, &checker_artifact_gate_markers);
    try requireInOrder(gate, &checker_artifact_gate_markers);
}

test "phase1 parity checker probes every artifact diff comparison mode" {
    const checker = try readRepoFile(std.testing.allocator, parity_checker_path);
    defer std.testing.allocator.free(checker);

    const gate = try functionBlock(checker, checker_artifact_gate_markers[0], "\n\ndef check_replay_routes");
    try requireAllOnce(gate, &checker_mode_probe_markers);
    try requireInOrder(gate, &checker_mode_probe_markers);
}

test "phase1 parity checker evaluates artifact diff before replay and fixture payloads" {
    const checker = try readRepoFile(std.testing.allocator, parity_checker_path);
    defer std.testing.allocator.free(checker);

    try requireInOrder(checker, &checker_collect_order_markers);
}

test "artifact diff helper still exposes the mode surface the parity checker probes" {
    const helper = try readRepoFile(std.testing.allocator, artifact_diff_path);
    defer std.testing.allocator.free(helper);

    try requireAllPresent(helper, &artifact_diff_public_markers);
}

test "phase1 parity artifact contract watches only checker and helper surfaces" {
    try std.testing.expectEqualStrings("scripts/zigux/check-phase1-parity.py", parity_checker_path);
    try std.testing.expectEqualStrings("scripts/zigux/artifact_diff.py", artifact_diff_path);
    try std.testing.expectEqual(@as(usize, 2), checker_path_markers.len);
    try std.testing.expectEqual(@as(usize, 5), checker_artifact_gate_markers.len);
    try std.testing.expectEqual(@as(usize, 6), checker_mode_probe_markers.len);
}
