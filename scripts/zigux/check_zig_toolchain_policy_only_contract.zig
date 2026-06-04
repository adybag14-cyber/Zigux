const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "policy-only CLI path validates policy before archive or zig probing" {
    try requireContains(checker_source, "parser.add_argument(\"--policy-only\", action=\"store_true\", help=\"Validate and summarize the pinned Zig policy without probing a zig executable.\")");
    try requireBefore(
        checker_source,
        "if args.policy_only:",
        "if args.archive_only:",
    );
    try requireBefore(
        checker_source,
        "if args.policy_only:",
        "zig = resolve_zig_executable(args.zig)",
    );
    try requireContains(checker_source, "emit_policy_summary()");
}

test "policy-only summary keeps machine-readable phase route and pin fields" {
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))");
}

test "policy-only invalid path fails closed with policy status and note" {
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=invalid\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={TOOLCHAIN_POLICY}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try requireContains(checker_source, "return 1");
}

test "pinned Phase 2 policy names the complete toolchain route handoff" {
    try requireContains(policy_source, "\"phase\": \"Phase 2\"");
    try requireContains(policy_source, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy_source, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy_source, "\"channel_minimum_lockstep\": true");
    try requireContains(policy_source, "\"archive_target_scope\"");
    try requireContains(policy_source, "\"x86_64-linux\"");
    try requireContains(policy_source, "\"required_make_routes\"");
    try requireContains(policy_source, "\"phase2-toolchain\"");
    try requireContains(policy_source, "\"phase2-tools\"");
    try requireContains(policy_source, "\"phase2-kconfig\"");
    try requireContains(policy_source, "\"phase2-cross\"");
    try requireContains(policy_source, "\"phase2-genksyms\"");
    try requireContains(policy_source, "\"phase2-fixdep\"");
    try requireContains(policy_source, "\"phase2-validate\"");
}
