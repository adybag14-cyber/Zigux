const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_archive_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "policy summary keeps pinned channel archive and route diagnostics" {
    try expectContains(checker_source, "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))");

    try expectBefore(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")", "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\"");
}

test "exact pinned channel remains enforced unless caller supplies an explicit minimum" {
    try expectContains(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");

    try expectBefore(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()", "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
    try expectBefore(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"", "return \"present\", None");
}

test "archive only path reports explicit policy archive evidence" {
    try expectContains(checker_source, "parser.add_argument(\"--archive-only\", action=\"store_true\", help=\"Validate the pinned Zig archive artifact without probing a zig executable.\")");
    try expectContains(checker_source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try expectContains(checker_source, "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
}

test "policy file pins the current trusted archive tuple and phase two routes" {
    try expectContains(policy_source, "\"phase\": \"Phase 2\"");
    try expectContains(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\": \"" ++ pinned_archive_sha256 ++ "\"");
    try expectContains(policy_source, "\"channel_minimum_lockstep\": true");
    try expectContains(policy_source, "\"archive_target_scope\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\"");
    try expectContains(policy_source, "\"required_make_routes\"");
    try expectContains(policy_source, "\"phase2-toolchain\"");
    try expectContains(policy_source, "\"phase2-validate\"");

    try expectBefore(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"", "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectBefore(policy_source, "\"archive_target_scope\"", "\"required_make_routes\"");
}
