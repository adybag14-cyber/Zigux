const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireBefore(earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, checker_source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, checker_source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit zig path normalization rejects missing paths and directories" {
    try requireContains("def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try requireContains("normalized = Path(explicit_zig).expanduser()");
    try requireContains("if not normalized.exists():");
    try requireContains("explicit zig path does not exist");
    try requireContains("if normalized.is_dir():");
    try requireContains("explicit zig path is a directory, expected an executable file");
}

test "explicit zig path bypasses repo local and PATH resolution after normalization" {
    try requireContains("def resolve_zig_executable(");
    try requireContains("if explicit_zig is not None:");
    try requireContains("return normalize_explicit_zig_path(explicit_zig)");
    try requireContains("return which(\"zig\")");
    try requireBefore("return normalize_explicit_zig_path(explicit_zig)", "pinned_channel = load_pinned_channel(policy_path)");
    try requireBefore("return normalize_explicit_zig_path(explicit_zig)", "return which(\"zig\")");
}

test "invalid explicit path keeps the CLI status envelope precise" {
    try requireContains("except ValueError as exc:");
    try requireContains("print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try requireContains("print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
}

test "self test protects the explicit missing path diagnostic" {
    try requireContains("expect_raises(lambda: normalize_explicit_zig_path(\"/tmp/zigux-toolchain-self-test-missing-zig\")");
    try requireContains("\"explicit zig path does not exist\"");
}
