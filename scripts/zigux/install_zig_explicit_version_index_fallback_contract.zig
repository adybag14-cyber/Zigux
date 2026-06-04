const std = @import("std");

const install_zig_text = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "explicit Zig version channels can resolve without the download index" {
    try expectContains(install_zig_text, "def load_index(channel: str) -> dict:");
    try expectContains(install_zig_text, "return read_index()");
    try expectContains(install_zig_text, "except (TimeoutError, urllib.error.URLError):");
    try expectContains(install_zig_text, "if not is_explicit_version(channel):");
    try expectContains(install_zig_text, "raise");
    try expectContains(install_zig_text, "return {}");
    try expectBefore(install_zig_text, "if not is_explicit_version(channel):", "return {}");
}

test "canonical release explicit channel bypasses the download index entry lookup" {
    try expectContains(install_zig_text, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
    try expectContains(install_zig_text, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')");
    try expectContains(install_zig_text, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')");
    try expectContains(install_zig_text, "if channel == CANONICAL_RELEASE_CHANNEL:");
    try expectContains(install_zig_text, "f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'");
    try expectContains(install_zig_text, "f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'");
    try expectContains(install_zig_text, "return target_key, channel, infer_tarball_url(channel, target_key, system_key)");
    try expectBefore(install_zig_text, "if channel == CANONICAL_RELEASE_CHANNEL:", "entry = index.get(channel)");
}

test "generic explicit dev versions still infer stable Zig build URLs" {
    try expectContains(install_zig_text, "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:");
    try expectContains(install_zig_text, "suffix = '.zip' if system_key == 'windows' else '.tar.xz'");
    try expectContains(install_zig_text, "if '-dev.' in channel:");
    try expectContains(install_zig_text, "https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}");
    try expectContains(install_zig_text, "https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}");
    try expectBefore(install_zig_text, "if channel == CANONICAL_RELEASE_CHANNEL:", "if '-dev.' in channel:");
    try expectBefore(install_zig_text, "if '-dev.' in channel:", "https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}");
}

test "fallback behavior is covered by installer self-test markers" {
    try expectContains(install_zig_text, "globals()['read_index'] = lambda: (_ for _ in ()).throw(TimeoutError('timed out'))");
    try expectContains(install_zig_text, "assert load_index('0.17.0-dev.758+748e7c5e3') == {}");
    try expectContains(install_zig_text, "load_index('master')");
    try expectContains(install_zig_text, "raise AssertionError('expected non-explicit channel timeout to fail')");
    try expectContains(install_zig_text, "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
}
