const std = @import("std");

const direct_cross_checker_path = "scripts/zigux/check-phase2-cross.py";
const cross_targets_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse {
        std.debug.panic("missing marker before order check: {s}", .{before});
    };
    const after_index = std.mem.indexOf(u8, haystack, after) orelse {
        std.debug.panic("missing marker after order check: {s}", .{after});
    };
    try std.testing.expect(before_index < after_index);
}

test "direct cross checker keeps public pass and grouped-fail markers" {
    const checker_text = try readRepoFile(direct_cross_checker_path);
    defer std.testing.allocator.free(checker_text);

    try requireContains(checker_text, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(checker_text, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try requireContains(checker_text, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(checker_text, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(checker_text, "{code}_START");
    try requireContains(checker_text, "{code}_END");
}

test "direct cross checker keeps fixture and Makefile issue vocabulary" {
    const checker_text = try readRepoFile(direct_cross_checker_path);
    defer std.testing.allocator.free(checker_text);

    try requireContains(checker_text, "MISSING_MAKEFILE_LINE");
    try requireContains(checker_text, "DUPLICATE_MAKEFILE_LINE");
    try requireContains(checker_text, "INVALID_FIXTURE_SHAPE");
    try requireContains(checker_text, "INVALID_FIXTURE_FIELD");
    try requireContains(checker_text, "ARCHIVE_SCOPE_MISMATCH");
    try requireContains(checker_text, "INVALID_CROSS_TARGET_ENTRY");
    try requireContains(checker_text, "DUPLICATE_CROSS_TARGET");
    try requireContains(checker_text, "INVALID_CROSS_TARGET_ROUTE");
    try requireContains(checker_text, "INVALID_CROSS_TARGET_MODE");
    try requireContains(checker_text, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
}

test "direct cross checker keeps primary input abort envelope covered by self-test" {
    const checker_text = try readRepoFile(direct_cross_checker_path);
    defer std.testing.allocator.free(checker_text);

    try requireContains(checker_text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(checker_text, "required file missing:");
    try requireContains(checker_text, "invalid json in required file:");
    try requireContains(checker_text, "invalid json shape in required file:");
    try requireContains(checker_text, "invalid upgrade_policy in required file:");
    try requireContains(checker_text, "invalid archive_target_scope in required file:");
    try requireContains(checker_text, "duplicate archive_target_scope entry in required file:");
    try requireContains(checker_text, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):");
}

test "direct cross checker preserves route and target-mode partition ordering" {
    const checker_text = try readRepoFile(direct_cross_checker_path);
    defer std.testing.allocator.free(checker_text);
    const fixture_text = try readRepoFile(cross_targets_path);
    defer std.testing.allocator.free(fixture_text);

    try requireContains(checker_text, "ROUTE = \"make -C zigux phase2-cross\"");
    try requireContains(checker_text, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try requireContains(checker_text, "archive_required_targets.add(target)");
    try requireInOrder(
        checker_text,
        "archive_target_scope = load_archive_target_scope(root)",
        "archive_required_targets: set[str] = set()",
    );

    try requireContains(fixture_text, "\"archive_target_scope\"");
    try requireContains(fixture_text, "\"target\": \"x86_64-linux\"");
    try requireContains(fixture_text, "\"validation_mode\": \"archive_required\"");
    try requireContains(fixture_text, "\"target\": \"aarch64-linux\"");
    try requireContains(fixture_text, "\"validation_mode\": \"route_contract_only\"");
}
