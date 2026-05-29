const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(1024 * 1024));
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit zig path diagnostics stay fail closed" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try expectContains(source, "parser.add_argument(\"--zig\"");
    try expectContains(source, "def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try expectContains(source, "return normalize_explicit_zig_path(explicit_zig)");
    try expectContains(source, "explicit zig path does not exist: {normalized}");
    try expectContains(source, "explicit zig path is a directory, expected an executable file: {normalized}");
    try expectContains(source, "ZIG_TOOLCHAIN_STATUS=invalid");
    try expectContains(source, "ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}");
    try expectContains(source, "ZIG_TOOLCHAIN_NOTE={exc}");
}

test "explicit zig validation happens before version probing" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try expectBefore(
        source,
        "if explicit_zig is not None:\n        return normalize_explicit_zig_path(explicit_zig)",
        "return which(\"zig\")",
    );
    try expectBefore(
        source,
        "zig = resolve_zig_executable(args.zig)",
        "version = read_zig_version(zig)",
    );
    try expectBefore(
        source,
        "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")",
        "return 1",
    );
}

test "explicit zig invalid output preserves pin-policy context" {
    const allocator = std.testing.allocator;
    const source = try readCheckerSource(allocator);
    defer allocator.free(source);

    try expectContains(source, "if expected_channel_raw is not None:");
    try expectContains(source, "ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}");
    try expectContains(source, "ZIG_TOOLCHAIN_PIN_POLICY=exact");
    try expectContains(source, "elif args.min_version is not None:");
    try expectContains(source, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only");
    try expectContains(source, "ZIG_TOOLCHAIN_PIN_POLICY=unresolved");
}
