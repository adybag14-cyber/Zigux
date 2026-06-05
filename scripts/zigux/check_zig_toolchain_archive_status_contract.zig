const std = @import("std");

const checker = @embedFile("check-zig-toolchain.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker, needle) != null);
}

fn expectOrder(needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, checker[cursor..], needle) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{needle});
            return error.MissingOrderedMarker;
        };
        cursor += found + needle.len;
    }
}

test "archive-only invalid policy path reports stable target and note fields" {
    try expectOrder(&.{
        "if args.archive_only:",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")",
        "return 1",
    });
}

test "archive-only missing archive reports expected metadata before note" {
    try expectOrder(&.{
        "message, search_roots_summary = describe_missing_archive(",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")",
        "return 0 if args.allow_missing else 1",
    });
}

test "archive-only explicit invalid path keeps expected filename and sha visible" {
    try expectOrder(&.{
        "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}\")",
        "return 1",
    });
}

test "archive validation present or mismatch output includes actual digest" {
    try expectOrder(&.{
        "archive_status, note, validated_expected_sha, actual_sha = validate_policy_archive(",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={note}\")",
    });
}

test "archive helper messages preserve current fail-closed wording" {
    try expectContains("return \"pinned Zig archive not found in archive search roots\", format_search_roots(search_roots)");
    try expectContains("return f\"explicit archive path does not exist: {resolved}\", None");
    try expectContains("f\"explicit archive path is a directory, expected a regular file: {archive_path}\"");
    try expectContains("f\"explicit archive path is not a regular file: {archive_path}\"");
    try expectContains("f\"expected archive filename {expected_filename} for {archive_target}, got {path.name}\"");
    try expectContains("f\"expected sha256 {expected_sha} for {archive_target}, got {actual_sha}\"");
    try expectContains("return \"present\", None, expected_sha, actual_sha");
}
