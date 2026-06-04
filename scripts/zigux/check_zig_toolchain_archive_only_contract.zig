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

test "archive-only CLI surface stays explicit and separate from zig probing" {
    try requireContains(checker_source, "parser.add_argument(\"--archive-only\", action=\"store_true\", help=\"Validate the pinned Zig archive artifact without probing a zig executable.\")");
    try requireContains(checker_source, "parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")");
    try requireContains(checker_source, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try requireBefore(
        checker_source,
        "if args.archive_only:",
        "\n    zig: str | None = None",
    );
    try requireBefore(
        checker_source,
        "if args.archive_only:",
        "zig = resolve_zig_executable(args.zig)",
    );
}

test "archive-only invalid and missing diagnostics keep machine-readable fields" {
    try requireContains(checker_source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try requireContains(checker_source, "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")");
    try requireContains(checker_source, "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try requireContains(checker_source, "return 0 if args.allow_missing else 1");
}

test "archive-only validation emits status path target expected and actual digest before failure note" {
    try requireBefore(
        checker_source,
        "archive_status, note, validated_expected_sha, actual_sha = validate_policy_archive(",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")",
    );
    try requireContains(
        checker_source,
        \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")
        \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}")
        \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
        \\        if expected_filename is not None:
        \\            print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
        \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")
        \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}")
        \\        if note is not None:
        \\            print(f"ZIG_TOOLCHAIN_NOTE={note}")
    );
    try requireContains(checker_source, "return 1");
    try requireContains(checker_source, "return 0");
}
