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

test "policy pins channel minimum and archive digest in lockstep" {
    try expectContains(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\": \"" ++ pinned_archive_sha256 ++ "\"");
    try expectContains(policy_source, "\"channel_minimum_lockstep\": true");
    try expectContains(policy_source, "\"archive_target_scope\"");
    try expectContains(policy_source, "\"required_make_routes\"");

    try expectBefore(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"", "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectBefore(policy_source, "\"channel_minimum_lockstep\": true", "\"archive_target_scope\"");
}

test "checker derives exact expected channel from policy unless minimum is explicit" {
    try expectContains(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(checker_source, "min_version_raw = args.min_version or load_min_version()");
    try expectContains(checker_source, "parse_zig_version(expected_channel_raw)");
    try expectContains(checker_source, "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");

    try expectBefore(checker_source, "min_version_raw = args.min_version or load_min_version()", "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectBefore(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()", "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
}

test "version evaluator rejects newer or release versions that are not the pinned channel" {
    try expectContains(checker_source, "def evaluate_toolchain_version(");
    try expectContains(checker_source, "if parsed_version < min_version:");
    try expectContains(checker_source, "return \"too_old\", None");
    try expectContains(checker_source, "if expected_channel_raw is not None:");
    try expectContains(checker_source, "if version.strip() != expected_channel_raw:");
    try expectContains(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try expectContains(checker_source, "return \"present\", None");

    try expectBefore(checker_source, "if parsed_version < min_version:", "if expected_channel_raw is not None:");
    try expectBefore(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"", "return \"present\", None");
}

test "CLI output keeps exact pin evidence visible in success and failure states" {
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={note}\")");
}
