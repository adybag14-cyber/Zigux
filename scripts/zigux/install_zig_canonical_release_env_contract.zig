const std = @import("std");

const source_path = "scripts/zigux/install-zig.py";

fn readInstaller(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, allocator, .limited(1024 * 1024));
}

fn containsAll(haystack: []const u8, needles: []const []const u8) bool {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) == null) return false;
    }
    return true;
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
}

test "canonical release constants are overridable by environment" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try std.testing.expect(containsAll(source, &.{
        "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
        "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')",
        "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')",
    }));
}

test "canonical release URL is gated to the pinned canonical channel" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const fn_start = try indexOfRequired(source, "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:");
    const canonical_gate = try indexOfRequired(source[fn_start..], "if channel == CANONICAL_RELEASE_CHANNEL:");
    const canonical_url = try indexOfRequired(source[fn_start..], "f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'");
    const dev_fallback = try indexOfRequired(source[fn_start..], "if '-dev.' in channel:");
    const builds_url = try indexOfRequired(source[fn_start..], "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'");
    const stable_url = try indexOfRequired(source[fn_start..], "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'");

    try std.testing.expect(canonical_gate < canonical_url);
    try std.testing.expect(canonical_url < dev_fallback);
    try std.testing.expect(dev_fallback < builds_url);
    try std.testing.expect(builds_url < stable_url);
}

test "canonical release resolve path bypasses download index lookup" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const resolve_start = try indexOfRequired(source, "def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:");
    const canonical_gate = try indexOfRequired(source[resolve_start..], "if channel == CANONICAL_RELEASE_CHANNEL:");
    const canonical_return = try indexOfRequired(source[resolve_start..], "return target_key, channel, infer_tarball_url(channel, target_key, system_key)");
    const index_lookup = try indexOfRequired(source[resolve_start..], "entry = index.get(channel)");
    const explicit_fallback = try indexOfRequired(source[resolve_start..], "if entry is None and VERSION_KEY_RE.fullmatch(channel):");

    try std.testing.expect(canonical_gate < canonical_return);
    try std.testing.expect(canonical_return < index_lookup);
    try std.testing.expect(index_lookup < explicit_fallback);
}
