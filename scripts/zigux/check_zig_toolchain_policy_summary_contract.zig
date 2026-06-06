const std = @import("std");

const ContractFile = struct {
    path: []const u8,
    contents: []u8,
};

const policy_summary_markers = [_][]const u8{
    "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:",
    "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")",
    "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")",
    "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")",
    "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")",
    "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}\")",
    "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}\")",
    "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))",
    "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))",
    "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))",
};

const policy_cli_markers = [_][]const u8{
    "parser.add_argument(\"--policy-only\", action=\"store_true\", help=\"Validate and summarize the pinned Zig policy without probing a zig executable.\")",
    "if args.policy_only:",
    "emit_policy_summary()",
    "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=invalid\")",
};

const current_policy_markers = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "\"channel\": \"0.17.0-dev.758+748e7c5e3\"",
    "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"",
    "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"",
    "\"channel_minimum_lockstep\": true",
    "\"archive_target_scope\"",
    "\"required_make_routes\"",
};

const required_make_routes = [_][]const u8{
    "\"phase2-toolchain\"",
    "\"phase2-tools\"",
    "\"phase2-kconfig\"",
    "\"phase2-cross\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    "\"phase2-validate\"",
};

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn loadFile(path: []const u8, limit: usize) !ContractFile {
    return .{
        .path = path,
        .contents = try readFile(path, limit),
    };
}

fn unloadFile(file: ContractFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectFileContains(file: ContractFile, needle: []const u8) !void {
    _ = file.path;
    try expectContains(file.contents, needle);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "policy-only summary keeps exact live output envelope" {
    const checker = try loadFile("scripts/zigux/check-zig-toolchain.py", 512 * 1024);
    defer unloadFile(checker);

    inline for (policy_summary_markers) |marker| {
        try expectFileContains(checker, marker);
    }
    inline for (policy_cli_markers) |marker| {
        try expectFileContains(checker, marker);
    }

    try expectBefore(
        checker.contents,
        "if args.policy_only:",
        "if args.archive_only:",
    );
    try expectBefore(
        checker.contents,
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))",
        "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))",
    );
    try expectBefore(
        checker.contents,
        "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))",
        "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))",
    );
}

test "policy file keeps Lane 03 exact pin and required route tuple" {
    const policy = try loadFile("scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    defer unloadFile(policy);

    inline for (current_policy_markers) |marker| {
        try expectFileContains(policy, marker);
    }
    inline for (required_make_routes) |route| {
        try expectFileContains(policy, route);
    }

    try expectBefore(policy.contents, "\"phase2-toolchain\"", "\"phase2-tools\"");
    try expectBefore(policy.contents, "\"phase2-tools\"", "\"phase2-kconfig\"");
    try expectBefore(policy.contents, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectBefore(policy.contents, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectBefore(policy.contents, "\"phase2-genksyms\"", "\"phase2-fixdep\"");
    try expectBefore(policy.contents, "\"phase2-fixdep\"", "\"phase2-validate\"");
}

test "self-test pins policy summary expectations inside checker tests" {
    const checker = try loadFile("scripts/zigux/check-zig-toolchain.py", 512 * 1024);
    defer unloadFile(checker);

    try expectFileContains(checker, "run_self_test");
    try expectFileContains(checker, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try expectFileContains(checker, "\"required_make_routes\": [\"phase2-toolchain\", \"phase2-validate\"]");
    try expectFileContains(checker, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"duplicate required_make_routes entry\")");
    try expectFileContains(checker, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"invalid required_make_routes\")");
}
