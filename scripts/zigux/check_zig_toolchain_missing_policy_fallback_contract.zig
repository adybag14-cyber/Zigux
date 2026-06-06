const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "missing policy keeps fallback minimum version explicit" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "FALLBACK_MIN_VERSION = \"0.16.0\"");
    try expectContains(source, "def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:");
    try expectContains(source, "if not policy_path.exists():\n        return None");
    try expectContains(source, "def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:");
    try expectOrdered(
        source,
        "payload = load_policy(policy_path)\n    if payload is None:\n        return fallback",
        "return str(payload[\"minimum_version\"])",
    );
}

test "policy-only mode reports missing policy without probing zig" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "if args.policy_only:");
    try expectContains(source, "emit_policy_summary()");
    try expectContains(source, "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=missing\")");
    try expectContains(source, "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")");
    try expectOrdered(source, "if args.policy_only:", "if args.archive_only:");
}

test "absent policy disables exact pin enforcement for executable checks" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "min_version_raw = args.min_version or load_min_version()");
    try expectContains(source, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectOrdered(
        source,
        "if expected_channel_raw is not None:\n        print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")",
        "else:\n        print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")",
    );
}

test "missing archive diagnostics remain separate from missing policy diagnostics" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def describe_missing_archive(");
    try expectContains(source, "pinned Zig archive not found in archive search roots");
    try expectContains(source, "format_search_roots(search_roots)");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
    try expectOrdered(
        source,
        "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=missing\")",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")",
    );
}
