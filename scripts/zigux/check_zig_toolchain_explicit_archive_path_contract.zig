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

test "explicit archive directory and non-regular paths are invalid before missing handling" {
    try expectContains(checker_source, "def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:");
    try expectContains(checker_source, "if archive_path.is_dir():");
    try expectContains(checker_source, "explicit archive path is a directory, expected a regular file");
    try expectContains(checker_source, "if not archive_path.is_file():");
    try expectContains(checker_source, "explicit archive path is not a regular file");
    try expectOrdered(
        checker_source,
        "if args.archive is not None and archive_path is not None:",
        "if archive_path is None or not archive_path.is_file():",
    );
}

test "invalid explicit archive path emits archive status and expected metadata" {
    try expectContains(checker_source, "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)");
    try expectContains(checker_source, "if invalid_archive_note is not None:");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}\")");
}

test "missing explicit archive keeps separate missing diagnostic" {
    try expectContains(checker_source, "def describe_missing_archive(");
    try expectContains(checker_source, "explicit archive path does not exist: {resolved}");
    try expectContains(checker_source, "pinned Zig archive not found in archive search roots");
    try expectContains(checker_source, "message, search_roots_summary = describe_missing_archive(");
    try expectContains(checker_source, "explicit_archive=args.archive");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
}

test "self-test keeps coverage for explicit archive diagnostics" {
    try expectContains(checker_source, "explicit_archive_dir = root / \"archive-dir\"");
    try expectContains(checker_source, "explicit_archive_dir.mkdir()");
    try expectContains(checker_source, "describe_invalid_explicit_archive_path(explicit_archive_dir)");
    try expectContains(checker_source, "missing_explicit_path = root / \"missing.tar.xz\"");
    try expectContains(checker_source, "describe_missing_archive(");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
}
