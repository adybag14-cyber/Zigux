const std = @import("std");
const testing = std.testing;

const installer = @embedFile("install-zig.py");
const policy = @embedFile("zig-toolchain-policy.json");

fn findAfter(haystack: []const u8, needle: []const u8, start: usize) !usize {
    const offset = std.mem.indexOf(u8, haystack[start..], needle) orelse {
        std.debug.print("missing marker after {d}: {s}\n", .{ start, needle });
        return error.MissingMarker;
    };
    return start + offset;
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    _ = try findAfter(source, needle, 0);
}

fn requireChain(source: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        cursor = try findAfter(source, marker, cursor);
        cursor += marker.len;
    }
}

test "installer canonical release constants stay aligned with the pinned policy" {
    try requireContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(
        installer,
        "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'",
    );
    try requireContains(
        installer,
        "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')",
    );
    try requireContains(
        installer,
        "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')",
    );
}

test "canonical release URL builder wins before generic Zig download paths" {
    try requireChain(installer, &.{
        "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
        "suffix = '.zip' if system_key == 'windows' else '.tar.xz'",
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'",
        "f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'",
        "if '-dev.' in channel:",
        "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
        "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
    });
}

test "resolver bypasses the public index for the canonical release channel" {
    try requireChain(installer, &.{
        "def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:",
        "target_key = f'{arch_key}-{system_key}'",
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
        "entry = index.get(channel)",
    });
}

test "installer self-test pins the exact canonical release URL" {
    try requireContains(
        installer,
        "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
    );
    try requireChain(installer, &.{
        "assert resolve_target(sample_index, '0.17.0-dev.758+748e7c5e3', 'x86_64', 'linux') ==",
        "'x86_64-linux',",
        "'0.17.0-dev.758+748e7c5e3',",
        "'https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz'",
    });
    try testing.expect(std.mem.indexOf(u8, installer, "https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz") == null);
}
