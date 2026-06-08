const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit archive target outside policy fails before archive existence checks" {
    try expectContains(checker_source, "def resolve_policy_archive(");
    try expectContains(checker_source, "explicit_target: str | None = None");
    try expectContains(checker_source, "if target is not None and target not in archive_targets:");
    try expectContains(checker_source, "f\"archive target {target!r} is outside archive_target_scope in {policy_path}: \"");
    try expectOrdered(
        checker_source,
        "if target is not None and target not in archive_targets:",
        "if explicit_archive is not None:",
    );
    try expectOrdered(
        checker_source,
        "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)",
        "if args.archive is not None and archive_path is not None:",
    );
}

test "archive-only invalid target reports invalid status and target echo" {
    try expectContains(checker_source, "except ValueError as exc:");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")");
    try expectContains(checker_source, "if args.archive_target is not None:");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectOrdered(
        checker_source,
        "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")",
    );
}

test "metadata validation rejects unpinned archive targets separately" {
    try expectContains(checker_source, "def expected_archive_metadata(");
    try expectContains(checker_source, "if archive_target not in payload[\"archive_sha256\"]:");
    try expectContains(checker_source, "f\"archive target {archive_target!r} is not pinned in {policy_path}\"");
    try expectContains(checker_source, "validate_policy_archive(duplicate_archive_path, \"aarch64-linux\", policy_path=policy_path)");
    try expectContains(checker_source, "\"is not pinned\"");
}

test "self-test keeps explicit target-scope coverage live" {
    try expectContains(checker_source, "expect_raises(");
    try expectContains(checker_source, "lambda: resolve_policy_archive(str(duplicate_archive_path), \"aarch64-linux\", root=root, policy_path=policy_path)");
    try expectContains(checker_source, "\"outside archive_target_scope\"");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
}
