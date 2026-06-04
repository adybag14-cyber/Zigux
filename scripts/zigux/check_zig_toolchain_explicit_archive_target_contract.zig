const std = @import("std");
const source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit archive target is required for multi-target policies" {
    try expectContains(source, "parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")");
    try expectContains(source, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try expectContains(source, "if explicit_archive is not None:");
    try expectContains(source, "if target is None:");
    try expectContains(source, "if len(archive_targets) != 1:");
    try expectContains(source, "raise ValueError(\"archive target must be explicit when policy covers multiple archive targets\")");

    try expectOrder(
        source,
        "if explicit_archive is not None:",
        "raise ValueError(\"archive target must be explicit when policy covers multiple archive targets\")",
    );
    try expectOrder(
        source,
        "raise ValueError(\"archive target must be explicit when policy covers multiple archive targets\")",
        "return target, Path(explicit_archive)",
    );
}

test "out-of-scope explicit archive targets fail before path validation" {
    try expectContains(source, "if target is not None and target not in archive_targets:");
    try expectContains(source, "f\"archive target {target!r} is outside archive_target_scope in {policy_path}: \"");
    try expectContains(source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")");
    try expectContains(source, "if args.archive_target is not None:");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")");

    try expectOrder(
        source,
        "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)",
        "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)",
    );
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
}

test "invalid explicit archive path diagnostics keep target metadata visible" {
    try expectContains(source, "def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:");
    try expectContains(source, "return f\"explicit archive path is a directory, expected a regular file: {archive_path}\"");
    try expectContains(source, "return f\"explicit archive path is not a regular file: {archive_path}\"");
    try expectContains(source, "if args.archive is not None and archive_path is not None:");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try expectContains(source, "return 1");

    try expectOrder(
        source,
        "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)",
        "print(f\"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}\")",
    );
    try expectOrder(
        source,
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}\")",
    );
}
