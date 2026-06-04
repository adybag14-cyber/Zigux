const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "archive-only branch resolves target and expected metadata before reporting" {
    try requireContains(checker_source, "parser.add_argument(\"--archive-only\", action=\"store_true\"");
    try requireContains(checker_source, "parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")");
    try requireContains(checker_source, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try requireContains(checker_source, "if args.archive_only:");
    try requireContains(checker_source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try requireContains(checker_source, "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
    try requireBefore(
        checker_source,
        "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)",
        "expected_sha, expected_filename = expected_archive_metadata(archive_target)",
    );
    try requireBefore(
        checker_source,
        "expected_sha, expected_filename = expected_archive_metadata(archive_target)",
        "if args.archive is not None and archive_path is not None:",
    );
}

test "missing or invalid archive reports stable fields before notes" {
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try requireContains(checker_source, "return 0 if args.allow_missing else 1");
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")",
    );
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")",
    );
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")",
        "return 0 if args.allow_missing else 1",
    );
}

test "validated archive reports expected and actual digest before mismatch note" {
    try requireContains(checker_source, "archive_status, note, validated_expected_sha, actual_sha = validate_policy_archive(");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")");
    try requireContains(checker_source, "if note is not None:");
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")",
    );
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")",
        "if note is not None:",
    );
    try requireBefore(
        checker_source,
        "if note is not None:",
        "return 0\n\n    zig: str | None = None",
    );
}
