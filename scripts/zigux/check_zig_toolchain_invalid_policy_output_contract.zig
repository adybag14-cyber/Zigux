const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "policy-only invalid policy emits dedicated policy envelope" {
    try expectContains(checker_source, "if args.policy_only:");
    try expectContains(checker_source, "emit_policy_summary()");
    try expectContains(checker_source, "except ValueError as exc:");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={TOOLCHAIN_POLICY}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectOrdered(
        checker_source,
        "if args.policy_only:",
        "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=invalid\")",
    );
}

test "executable probe invalid policy emits toolchain envelope" {
    try expectContains(checker_source, "zig = resolve_zig_executable(args.zig)");
    try expectContains(checker_source, "min_version_raw = args.min_version or load_min_version()");
    try expectContains(checker_source, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try expectOrdered(
        checker_source,
        "zig = resolve_zig_executable(args.zig)",
        "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")",
    );
}

test "invalid policy loaders keep concrete failure reasons visible" {
    try expectContains(checker_source, "raise ValueError(f\"invalid toolchain policy JSON in {policy_path}: {exc.msg}\")");
    try expectContains(checker_source, "raise ValueError(f\"invalid toolchain policy payload in {policy_path}: expected object\")");
    try expectContains(checker_source, "duplicate toolchain policy keys in {policy_path}: ");
    try expectContains(checker_source, "unexpected toolchain policy keys in {policy_path}: ");
    try expectContains(checker_source, "invalid archive_sha256 in {policy_path}");
    try expectContains(checker_source, "minimum_version must match channel when channel_minimum_lockstep is true");
}

test "self-test still exercises representative invalid policy branches" {
    try expectContains(checker_source, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"invalid minimum_version\")");
    try expectContains(checker_source, "expect_raises(lambda: load_pinned_channel(policy_path), \"invalid channel\")");
    try expectContains(checker_source, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"invalid archive_sha256[x86_64-linux]\")");
    try expectContains(checker_source, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"duplicate toolchain policy keys\")");
    try expectContains(checker_source, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"unexpected toolchain policy keys\")");
    try expectContains(checker_source, "expect_raises(lambda: load_min_version(policy_path, \"0.15.0\"), \"invalid toolchain policy JSON\")");
}
