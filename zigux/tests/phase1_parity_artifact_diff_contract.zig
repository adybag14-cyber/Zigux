const std = @import("std");

const max_file_size = 512 * 1024;

fn readFileAlloc(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectAnyContains(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }
    try std.testing.expect(false);
}

test "phase1 parity checker keeps the committed fixture and artifact diff helper wired" {
    const checker = try readFileAlloc("scripts/zigux/check-phase1-parity.py");
    defer std.testing.allocator.free(checker);

    const required_paths = [_][]const u8{
        "zigux/tests/fixtures/phase1_helpers.json",
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "scripts/zigux/artifact_diff.py",
    };
    for (required_paths) |path| {
        try expectContains(checker, path);
    }
    try expectContains(checker, "PHASE1_PARITY_SELF_TEST_CASE_COUNT");

    const expected_sections = [_][]const u8{
        "\"find_bit\"",
        "\"bitmap\"",
        "\"string\"",
        "\"rbtree\"",
        "\"argv_split\"",
        "\"cmdline\"",
        "\"ctype\"",
        "\"hweight\"",
        "\"list_sort\"",
        "\"zalloc\"",
        "\"str_error_r\"",
        "\"slab\"",
        "\"vsprintf\"",
    };
    for (expected_sections) |section| {
        try expectContains(checker, section);
    }

    try expectContains(checker, "PHASE1_PARITY_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_PARITY=pass");
    try expectContains(checker, "artifact_diff_path");
}

test "phase1 parity and artifact diff gates keep fail closed marker catalogs visible" {
    const parity_checker = try readFileAlloc("scripts/zigux/check-phase1-parity.py");
    defer std.testing.allocator.free(parity_checker);
    const artifact_helper = try readFileAlloc("scripts/zigux/artifact_diff.py");
    defer std.testing.allocator.free(artifact_helper);
    const artifact_contract = try readFileAlloc("scripts/zigux/check-artifact-diff-contract.py");
    defer std.testing.allocator.free(artifact_contract);

    const parity_issue_markers = [_][]const u8{
        "PHASE1_PARITY_INPUT_ISSUES_START",
        "PHASE1_PARITY_INPUT_ISSUES_END",
        "PHASE1_PARITY_OUTPUT_ISSUES_START",
        "PHASE1_PARITY_OUTPUT_ISSUES_END",
        "PHASE1_PARITY_KEY_ISSUES_START",
        "PHASE1_PARITY_KEY_ISSUES_END",
        "PHASE1_PARITY_REFRESH=pass",
    };
    for (parity_issue_markers) |marker| {
        try expectContains(parity_checker, marker);
    }

    try expectContains(artifact_helper, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
    try expectContains(artifact_helper, "ARTIFACT_DIFF_SELF_TEST_CASES=");
    try expectContains(artifact_contract, "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=");
    try expectContains(artifact_contract, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=");
    try expectContains(artifact_contract, "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=");
    try expectContains(artifact_contract, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=");
    try expectContains(artifact_contract, "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=");

    try expectAnyContains(artifact_contract, &.{
        "\"cli_missing_mode_value\"",
        "\"cli_invalid_mode\"",
    });
    try expectAnyContains(artifact_contract, &.{
        "\"bytes_missing_both\"",
        "\"sha256_missing_both\"",
    });
}

test "phase1 committed fixture and manifest keep helper coverage aligned" {
    const fixture = try readFileAlloc("zigux/tests/fixtures/phase1_helpers.json");
    defer std.testing.allocator.free(fixture);
    const manifest = try readFileAlloc("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    const helpers = [_][]const u8{
        "tools/lib/argv_split.zig",
        "tools/lib/bitmap.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/string.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    };
    for (helpers) |helper| {
        try expectContains(manifest, helper);
    }

    try expectContains(manifest, "\"helper_count\": 13");
    try expectContains(manifest, "\"status\": \"closed\"");
    try expectContains(manifest, "\"shared_replay_parked_helpers\"");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");

    const fixture_sections = [_][]const u8{
        "\"find_bit\"",
        "\"bitmap\"",
        "\"string\"",
        "\"rbtree\"",
        "\"argv_split\"",
        "\"cmdline\"",
        "\"ctype\"",
        "\"hweight\"",
        "\"list_sort\"",
        "\"zalloc\"",
        "\"str_error_r\"",
        "\"slab\"",
        "\"vsprintf\"",
    };
    for (fixture_sections) |section| {
        try expectCount(fixture, section, 1);
    }

    try expectAnyContains(fixture, &.{
        "\"tail_andnot_clamped_exhausted\"",
        "\"tail_clamped_empty_last\"",
    });
    try expectAnyContains(fixture, &.{
        "\"copy_clear_tail_values\"",
        "\"alloc_words\"",
    });
    try expectContains(fixture, "\"replace_char_cstr_bytes\"");
    try expectContains(fixture, "\"bool_sorted_ordinals\"");
}

test "artifact diff gate keeps binary diff mode and review coverage visible" {
    const helper = try readFileAlloc("scripts/zigux/artifact_diff.py");
    defer std.testing.allocator.free(helper);
    const contract = try readFileAlloc("scripts/zigux/check-artifact-diff-contract.py");
    defer std.testing.allocator.free(contract);
    const note = try readFileAlloc("Documentation/zigux/artifact-diff.md");
    defer std.testing.allocator.free(note);

    try expectAnyContains(helper, &.{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "--mode {text,json,sha256}",
        "unsupported artifact diff mode",
    });
    try expectAnyContains(helper, &.{
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "sha256_pass",
    });
    try expectAnyContains(helper, &.{
        "\"legacy_sha256_alias\"",
        "sha256_drift",
    });
    try expectAnyContains(helper, &.{
        "\"missing_mode_value_rejected\"",
        "invalid_mode_rejected",
    });
    try expectAnyContains(helper, &.{
        "\"extra_positional_rejected\"",
        "invalid_mode_rejected",
    });
    try expectContains(helper, "ARTIFACT_DIFF_SELF_TEST=pass");

    try expectAnyContains(contract, &.{
        "BASE_CONTRACT_CASES = [",
        "EXPECTED_CONTRACT_CASES = [",
    });
    try expectContains(contract, "REPEAT_CONTRACT_CASES = [");
    try expectAnyContains(contract, &.{
        "\"bytes_pass\"",
        "\"sha256_pass\"",
    });
    try expectAnyContains(contract, &.{
        "\"bytes_drift_repeat\"",
        "\"sha256_drift_repeat\"",
    });
    try expectAnyContains(contract, &.{
        "\"cli_extra_positional_args\"",
        "\"cli_invalid_mode\"",
    });
    try expectContains(contract, "ARTIFACT_DIFF_CONTRACT=pass");

    try expectContains(note, "scripts/zigux/artifact_diff.py");
    try expectContains(note, "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`");
    try expectContains(note, "rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`");
}
