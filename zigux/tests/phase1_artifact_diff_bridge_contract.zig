const std = @import("std");

const allocator = std.testing.allocator;

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn has(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase 1 artifact-diff helper keeps current bytes mode and parser contract" {
    const artifact_diff = try readRepoFile("scripts/zigux/artifact_diff.py", 64 * 1024);
    defer allocator.free(artifact_diff);

    const current_bytes_mode = has(artifact_diff, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    const legacy_sha256_mode = has(artifact_diff, "mode == 'sha256'");

    try std.testing.expect(current_bytes_mode or legacy_sha256_mode);
    try expectContains(artifact_diff, "ARTIFACT_DIFF=pass");
    try expectContains(artifact_diff, "MODE=");
    try expectContains(artifact_diff, "EXPECTED=");
    try expectContains(artifact_diff, "ACTUAL=");
    try expectContains(artifact_diff, "SHA256=");
    try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST=pass");

    if (current_bytes_mode) {
        try expectContains(artifact_diff, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
        try expectContains(artifact_diff, "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]");
        try expectContains(artifact_diff, "INVALID_MODE_ERROR_TEMPLATE");
        try expectContains(artifact_diff, "\"legacy_sha256_alias\"");
        try expectContains(artifact_diff, "\"missing_mode_value_rejected\"");
        try expectContains(artifact_diff, "\"extra_positional_rejected\"");
        try expectContains(artifact_diff, "def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:");
        try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}");
        try expectNotContains(artifact_diff, "--mode {text,json,sha256}");
    } else {
        try expectContains(artifact_diff, "parser.add_argument('--mode', choices=['text', 'json', 'sha256'])");
        try expectContains(artifact_diff, "def compare_artifacts(mode: str, expected: Path, actual: Path)");
    }
}

test "phase 1 parity checker depends on artifact-diff JSON comparison gate" {
    const parity_checker = try readRepoFile("scripts/zigux/check-phase1-parity.py", 192 * 1024);
    defer allocator.free(parity_checker);

    try expectContains(parity_checker, "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.py\")");
    try expectContains(parity_checker, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try expectContains(parity_checker, "HARNESS_REL = Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")");
    try expectContains(parity_checker, "phase1_helpers");
    try expectContains(parity_checker, "actual");
    try expectContains(parity_checker, "\"--mode\",");
    try expectContains(parity_checker, "\"json\",");
    try expectContains(parity_checker, "ARTIFACT_DIFF_REL");
}

test "phase 1 workflow keeps artifact-diff gates ordered as a deterministic replay block" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 256 * 1024);
    defer allocator.free(workflow);

    const artifact_step = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/artifact_diff.py --self-test") orelse
        return error.MissingArtifactDiffSelfTest;

    if (std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test")) |contract_self_test| {
        const contract_check = std.mem.indexOfPos(u8, workflow, contract_self_test + 1, "run: python3 scripts/zigux/check-artifact-diff-contract.py") orelse
            return error.MissingArtifactDiffContractCheck;
        const determinism_self_test = std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test") orelse
            return error.MissingArtifactDiffDeterminismSelfTest;
        try std.testing.expect(artifact_step < contract_self_test);
        try std.testing.expect(contract_self_test < contract_check);
        try std.testing.expect(contract_check < determinism_self_test);
    }

    if (std.mem.indexOf(u8, workflow, "run: python3 scripts/zigux/check-phase1-parity.py")) |parity_step| {
        try std.testing.expect(artifact_step < parity_step);
    }
}
