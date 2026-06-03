const std = @import("std");

const source = @embedFile("install-zig.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "canonical release settings stay pinned to the Zigux release mirror" {
    try requireContains("CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
    try requireContains("CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')");
    try requireContains("CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')");
    try requireContains("f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'");
    try requireContains("f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'");
}

test "canonical release path is checked before generic dev and stable fallbacks" {
    try requireOrder("if channel == CANONICAL_RELEASE_CHANNEL:", "if '-dev.' in channel:");
    try requireOrder("if '-dev.' in channel:", "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'");
}

test "resolve target bypasses the download index for the canonical channel" {
    try requireOrder(
        "target_key = f'{arch_key}-{system_key}'",
        "if channel == CANONICAL_RELEASE_CHANNEL:\n        return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
    );
    try requireOrder(
        "if channel == CANONICAL_RELEASE_CHANNEL:\n        return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
        "entry = index.get(channel)",
    );
    try requireContains("'https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz'");
}
