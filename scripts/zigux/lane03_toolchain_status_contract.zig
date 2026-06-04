const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireMarker(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        return error.MissingMarker;
    }
}

fn hasMarker(source: []const u8, marker: []const u8) bool {
    return std.mem.indexOf(u8, source, marker) != null;
}

fn requireOneOf(source: []const u8, first: []const u8, second: []const u8) !void {
    if (!hasMarker(source, first) and !hasMarker(source, second)) {
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingMarker;
    try std.testing.expect(first_index < second_index);
}

test "lane03 toolchain checker keeps executable status output explicit" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_STATUS=missing\")");
    try requireMarker(checker, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");
    try requireOneOf(
        checker,
        "print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_PATH={zig or 'unresolved'}\")",
    );
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    if (hasMarker(checker, "describe_missing_zig(")) {
        try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
    }
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try requireOrdered(
        checker,
        "version = read_zig_version(zig)",
        "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)",
    );
}

test "lane03 toolchain checker keeps archive status output explicit" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    if (!hasMarker(checker, "--archive-only")) return;

    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try requireMarker(checker, "return 0 if args.allow_missing else 1");
    try requireOrdered(
        checker,
        "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")",
    );
}

test "lane03 self-test covers status and archive failure cases" {
    const checker = try readRepoFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    if (hasMarker(checker, "normalize_explicit_zig_path(")) {
        try requireMarker(checker, "\"explicit zig path does not exist\"");
    }
    try requireMarker(checker, "read_zig_version(");
    try requireMarker(checker, "\"zig version command returned empty output\"");
    try requireMarker(checker, "\"zig version command failed: permission denied\"");
    if (hasMarker(checker, "--archive-only")) {
        try requireMarker(checker, "explicit archive path is a directory, expected a regular file");
        try requireMarker(checker, "\"multiple repo-local pinned archive candidates matched\"");
        try requireMarker(checker, "\"expected sha256 {expected_archive_sha} for x86_64-linux, got {drift_sha}\"");
        try requireMarker(checker, "\"minimum_version must match channel\"");
        try requireMarker(checker, "\"duplicate required_make_routes entry\"");
    }
}
