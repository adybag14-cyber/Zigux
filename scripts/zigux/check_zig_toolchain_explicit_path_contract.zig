const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit zig path is normalized before any fallback lookup" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try expectContains(checker, "normalized = Path(explicit_zig).expanduser()");
    try expectContains(checker, "if not normalized.exists():");
    try expectContains(checker, "raise ValueError(f\"explicit zig path does not exist: {normalized}\")");
    try expectContains(checker, "if normalized.is_dir():");
    try expectContains(checker, "raise ValueError(f\"explicit zig path is a directory, expected an executable file: {normalized}\")");
    try expectContains(checker, "return str(normalized)");
    try expectOrdered(
        checker,
        "if explicit_zig is not None:\n        return normalize_explicit_zig_path(explicit_zig)",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
}

test "invalid explicit zig path reports the stable toolchain status envelope" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectOrdered(
        checker,
        "except ValueError as exc:\n        print(\"ZIG_TOOLCHAIN_STATUS=invalid\")",
        "print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")",
    );
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectOrdered(
        checker,
        "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")",
        "return 1",
    );
}

test "self-test covers missing explicit path and executable failure reports" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "expect_raises(lambda: normalize_explicit_zig_path(\"/tmp/zigux-toolchain-self-test-missing-zig\"), \"explicit zig path does not exist\")");
    try expectContains(checker, "runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError(\"missing\")),");
    try expectContains(checker, "\"zig executable not found\"");
    try expectContains(checker, "stderr=\"permission denied\\n\",");
    try expectContains(checker, "\"zig version command failed: permission denied\"");
    try expectContains(checker, "stdout=\"\\n\",");
    try expectContains(checker, "\"zig version command returned empty output\"");
    try expectContains(checker, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try expectContains(checker, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
}
