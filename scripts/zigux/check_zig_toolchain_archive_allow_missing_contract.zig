const std = @import("std");

const CHECKER_PATH = "scripts/zigux/check-zig-toolchain.py";
const POLICY_PATH = "scripts/zigux/zig-toolchain-policy.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "archive-only allow-missing is a distinct parser surface" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "\"--archive-only\"");
    try expectContains(checker, "Validate the pinned Zig archive artifact without probing a zig executable.");
    try expectContains(checker, "\"--allow-missing\"");
    try expectContains(checker, "Return success when zig is unavailable.");
    try expectContains(checker, "\"--archive-target\"");
    try expectContains(checker, "Archive target key from scripts/zigux/zig-toolchain-policy.json.");
}

test "archive-only dispatch precedes executable probing" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectBefore(checker, "if args.self_test:", "if args.archive_only:");
    try expectBefore(checker, "if args.policy_only:", "if args.archive_only:");
    try expectBefore(checker, "if args.archive_only:", "zig: str | None = None");
    try expectContains(checker, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try expectContains(checker, "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
}

test "missing archive envelope stays informative and allow-missing only changes exit code" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "if archive_path is None or not archive_path.is_file():");
    try expectContains(checker, "message, search_roots_summary = describe_missing_archive(");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectContains(checker, "return 0 if args.allow_missing else 1");
    try expectBefore(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")", "return 0 if args.allow_missing else 1");
}

test "current policy supplies the allow-missing archive identity" {
    const policy = try readFile(std.testing.allocator, POLICY_PATH);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
}
