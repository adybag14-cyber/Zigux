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
    const artifact_diff = try readRepoFile("scripts/zigux/artifact_diff.zig", 64 * 1024);
    defer allocator.free(artifact_diff);

    const current_bytes_mode = has(artifact_diff, "pub const Mode = enum {") and
        has(artifact_diff, ".bytes,");

    try std.testing.expect(current_bytes_mode);
    try expectContains(artifact_diff, "ARTIFACT_DIFF={s}");
    try expectContains(artifact_diff, "MODE={s}");
    try expectContains(artifact_diff, "EXPECTED={s}");
    try expectContains(artifact_diff, "ACTUAL={s}");
    try expectContains(artifact_diff, "SHA256={s}");
    try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST=pass");

    try expectContains(artifact_diff, "if (std.mem.eql(u8, raw, \"sha256\")) return .bytes;");
    try expectContains(artifact_diff, "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test]");
    try expectContains(artifact_diff, "invalid choice: '{s}' (choose from text, json, bytes)");
    try expectContains(artifact_diff, "\"legacy_sha256_alias\"");
    try expectContains(artifact_diff, "\"missing_mode_value_rejected\"");
    try expectContains(artifact_diff, "\"extra_positional_rejected\"");
    try expectContains(artifact_diff, "pub fn compareBytes(io: Io, allocator: std.mem.Allocator, expected_path: []const u8, actual_path: []const u8)");
    try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={d}");
    try expectNotContains(artifact_diff, "--mode {text,json,sha256}");
}

test "phase 1 parity checker depends on artifact-diff JSON comparison gate" {
    const parity_checker = try readRepoFile("scripts\zigux/check_phase1_parity.zig", 192 * 1024);
    defer allocator.free(parity_checker);

    try expectContains(parity_checker, "ARTIFACT_DIFF_REL = Path(\"scripts/zigux/artifact_diff.zig\")");
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

    const artifact_step = std.mem.indexOf(u8, workflow, "run: zig run scripts/zigux/artifact_diff.zig -- --self-test") orelse
        return error.MissingArtifactDiffSelfTest;

    if (std.mem.indexOf(u8, workflow, "run: zig run scripts/zigux/check_artifact_diff_contract.zig -- --self-test")) |contract_self_test| {
        const contract_check = std.mem.indexOfPos(u8, workflow, contract_self_test + 1, "run: zig run scripts/zigux/check_artifact_diff_contract.zig") orelse
            return error.MissingArtifactDiffContractCheck;
        const determinism_self_test = std.mem.indexOf(u8, workflow, "run: zig run scripts/zigux/check_phase4_artifact_diff_determinism.zig -- --self-test") orelse
            return error.MissingArtifactDiffDeterminismSelfTest;
        try std.testing.expect(artifact_step < contract_self_test);
        try std.testing.expect(contract_self_test < contract_check);
        try std.testing.expect(contract_check < determinism_self_test);
    }

    if (std.mem.indexOf(u8, workflow, "run: zig run scripts/zigux/check_phase1_parity.zig")) |parity_step| {
        try std.testing.expect(artifact_step < parity_step);
    }
}