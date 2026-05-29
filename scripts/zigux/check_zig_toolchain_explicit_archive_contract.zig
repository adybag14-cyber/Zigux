const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "explicit archive CLI stays wired into archive-only validation" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "parser.add_argument(\"--archive-only\"");
    try expectContains(source, "parser.add_argument(\"--archive\"");
    try expectContains(source, "parser.add_argument(\"--archive-target\"");
    try expectContains(source, "resolve_policy_archive(args.archive, args.archive_target)");
    try expectContains(source, "expected_archive_metadata(archive_target)");
    try expectContains(source, "validate_policy_archive(\n                archive_path,");

    try expectOrdered(
        source,
        "if args.archive_only:",
        "resolve_policy_archive(args.archive, args.archive_target)",
    );
    try expectOrdered(
        source,
        "resolve_policy_archive(args.archive, args.archive_target)",
        "validate_policy_archive(\n                archive_path,",
    );
}

test "explicit archive failures report precise path and target context" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:");
    try expectContains(source, "explicit archive path is a directory, expected a regular file");
    try expectContains(source, "explicit archive path is not a regular file");
    try expectContains(source, "explicit archive path does not exist: {resolved}");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}");
}

test "explicit archive mode avoids misleading search-root diagnostics" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def describe_missing_archive(");
    try expectContains(source, "if explicit_archive is not None:");
    try expectContains(source, "return f\"explicit archive path does not exist: {resolved}\", None");
    try expectContains(source, "return \"pinned Zig archive not found in archive search roots\", format_search_roots(search_roots)");
    try expectContains(source, "if search_roots_summary is not None:");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}");
    try expectContains(source, "archive target {target!r} is outside archive_target_scope");

    try expectOrdered(
        source,
        "if explicit_archive is not None:",
        "return f\"explicit archive path does not exist: {resolved}\", None",
    );
    try expectOrdered(
        source,
        "if search_roots_summary is not None:",
        "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}",
    );
}
