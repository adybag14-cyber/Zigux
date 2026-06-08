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

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "min-version override switches checker to minimum-only pin policy" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "\"--min-version\"");
    try expectContains(checker, "Minimum supported Zig version string.");
    try expectContains(checker, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(checker, "elif args.min_version is not None:");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectBefore(
        checker,
        "min_version_raw = args.min_version",
        "expected_channel_raw = None if args.min_version else load_pinned_channel()",
    );
}

test "exact pinned-channel enforcement remains policy-driven only" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "def evaluate_toolchain_version(");
    try expectContains(checker, "expected_channel_raw: str | None = None");
    try expectContains(checker, "if expected_channel_raw is not None:");
    try expectContains(checker, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try expectBefore(checker, "if parsed_version < min_version:", "if expected_channel_raw is not None:");
}

test "override diagnostics omit pinned-channel output while preserving invalid state" {
    const checker = try readFile(std.testing.allocator, CHECKER_PATH);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContains(checker, "if expected_channel_raw is not None:");
    try expectContains(checker, "elif args.min_version is not None:");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
}

test "current policy still pins phase2 exact channel separately" {
    const policy = try readFile(std.testing.allocator, POLICY_PATH);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
    try expectNotContains(policy, "\"minimum_only\"");
}
