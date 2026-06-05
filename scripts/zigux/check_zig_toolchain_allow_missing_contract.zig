const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_offset = std.mem.indexOf(u8, haystack[before_index..], after) orelse return error.MissingAfterMarker;
    try std.testing.expect(after_offset > 0);
}

test "allow-missing flag is explicit and scoped to missing dependencies" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(
        checker,
        "parser.add_argument(\"--allow-missing\", action=\"store_true\", help=\"Return success when zig is unavailable.\")",
    );
    try expectContains(checker, "return 0 if args.allow_missing else 1");
    try expectContains(checker, "ZIG_TOOLCHAIN_STATUS=missing");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
}

test "invalid checker states still fail independently of allow-missing" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const archive_invalid_status = "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")";
    const toolchain_invalid_status = "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")";

    try expectInOrder(checker, "except ValueError as exc:", archive_invalid_status);
    try expectInOrder(checker, archive_invalid_status, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectInOrder(checker, archive_invalid_status, "return 1");
    try expectInOrder(checker, "except ValueError as exc:", toolchain_invalid_status);
    try expectInOrder(checker, toolchain_invalid_status, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectInOrder(checker, toolchain_invalid_status, "return 1");
}

test "missing archive reports policy metadata before allow-missing exit" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const archive_block_start = "if archive_path is None or not archive_path.is_file():";
    const archive_exit = "return 0 if args.allow_missing else 1";

    try expectInOrder(checker, archive_block_start, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try expectInOrder(checker, archive_block_start, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")");
    try expectInOrder(checker, archive_block_start, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectInOrder(checker, archive_block_start, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try expectInOrder(checker, archive_block_start, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectInOrder(checker, archive_block_start, archive_exit);
}

test "missing zig reports search roots and pin policy before allow-missing exit" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const missing_zig_block = "if zig is None:";
    const missing_zig_exit = "return 0 if args.allow_missing else 1";

    try expectInOrder(checker, missing_zig_block, "message, search_roots_summary = describe_missing_zig(");
    try expectInOrder(checker, missing_zig_block, "print(\"ZIG_TOOLCHAIN_STATUS=missing\")");
    try expectInOrder(checker, missing_zig_block, "print(\"ZIG_TOOLCHAIN_PATH=unresolved\")");
    try expectInOrder(checker, missing_zig_block, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try expectInOrder(checker, missing_zig_block, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectInOrder(checker, missing_zig_block, "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
    try expectInOrder(checker, missing_zig_block, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectInOrder(checker, missing_zig_block, missing_zig_exit);
}

test "policy still pins the exact phase two toolchain channel" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
}
