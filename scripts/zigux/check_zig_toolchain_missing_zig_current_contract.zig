const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "missing zig path emits structured bootstrap diagnostics" {
    try expectContains(checker_source, "def describe_missing_zig(");
    try expectContains(checker_source, "zig not found on PATH or in repo-local toolchain search roots");
    try expectContains(checker_source, "for pinned channel {pinned_channel}");
    try expectContains(checker_source, "format_search_roots(search_roots)");

    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_STATUS=missing\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PATH=unresolved\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectContains(checker_source, "return 0 if args.allow_missing else 1");
}

test "missing zig diagnostics are emitted in reviewable order" {
    try expectBefore(checker_source, "print(\"ZIG_TOOLCHAIN_STATUS=missing\")", "print(\"ZIG_TOOLCHAIN_PATH=unresolved\")");
    try expectBefore(checker_source, "print(\"ZIG_TOOLCHAIN_PATH=unresolved\")", "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try expectBefore(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")", "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
    try expectBefore(checker_source, "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")", "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectBefore(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")", "return 0 if args.allow_missing else 1");
}

test "min-version override keeps missing zig policy minimum-only" {
    try expectContains(checker_source, "parser.add_argument(\n        \"--min-version\",");
    try expectContains(checker_source, "parser.add_argument(\"--allow-missing\", action=\"store_true\"");
    try expectContains(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()");

    try expectBefore(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()", "if zig is None:");
    try expectBefore(checker_source, "if expected_channel_raw is not None:\n            print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")", "else:\n            print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
}

test "pinned policy channel remains the missing zig default" {
    try expectContains(policy_source, "\"phase\": \"Phase 2\"");
    try expectContains(policy_source, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_source, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_source, "\"channel_minimum_lockstep\": true");
    try expectContains(policy_source, "\"phase2-toolchain\"");
    try expectContains(policy_source, "\"phase2-validate\"");
}
