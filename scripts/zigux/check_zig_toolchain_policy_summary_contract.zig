const std = @import("std");

const max_file_bytes = 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    const fd = try std.posix.openat(std.posix.AT.FDCWD, path, .{ .ACCMODE = .RDONLY }, 0);
    defer std.Io.Threaded.closeFd(fd);

    var contents = std.ArrayList(u8).empty;
    errdefer contents.deinit(allocator);

    var buffer: [4096]u8 = undefined;
    while (true) {
        const read_count = try std.posix.read(fd, &buffer);
        if (read_count == 0) break;
        if (contents.items.len + read_count > max_file_bytes) return error.FileTooLarge;
        try contents.appendSlice(allocator, buffer[0..read_count]);
    }
    return try contents.toOwnedSlice(allocator);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

test "policy-only summary emits stable public status keys" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectContains(checker, "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=missing\")");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}\")");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))");
    try expectContains(checker, "parser.add_argument(\"--policy-only\", action=\"store_true\"");
    try expectContains(checker, "if args.policy_only:");
    try expectContains(checker, "emit_policy_summary()");
}

test "bootstrap workflow keeps exactly one policy-only checker hook" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectCount(
        workflow,
        "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        1,
    );
    try expectContains(workflow, "- name: Check current Zig toolchain policy packet");
    try expectContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
}

test "policy packet exposes fields consumed by policy summary" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"archive_sha256\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
}
