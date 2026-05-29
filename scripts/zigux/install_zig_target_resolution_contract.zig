const std = @import("std");

const installer = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "installer keeps platform normalization narrow and explicit" {
    try expectContains(installer, "def normalize_os(name: str) -> str:");
    try expectContains(installer, "lowered.startswith('linux')");
    try expectContains(installer, "lowered.startswith('darwin') or lowered.startswith('mac')");
    try expectContains(installer, "lowered.startswith('windows')");
    try expectContains(installer, "unsupported OS for Zig installer: {name}");

    try expectContains(installer, "def normalize_arch(name: str) -> str:");
    try expectContains(installer, "{'amd64', 'x86_64', 'x64'}");
    try expectContains(installer, "{'arm64', 'aarch64'}");
    try expectContains(installer, "{'x86', 'i386', 'i686'}");
    try expectContains(installer, "unsupported architecture for Zig installer: {name}");
}

test "installer can infer explicit-version archive URLs without the download index" {
    try expectContains(installer, "VERSION_KEY_RE = re.compile");
    try expectContains(installer, "def is_explicit_version(channel: str) -> bool:");
    try expectContains(installer, "return VERSION_KEY_RE.fullmatch(channel) is not None");

    try expectContains(installer, "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:");
    try expectContains(installer, "suffix = '.zip' if system_key == 'windows' else '.tar.xz'");
    try expectContains(installer, "if '-dev.' in channel:");
    try expectContains(installer, "https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}");
    try expectContains(installer, "https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}");

    try expectContains(installer, "if entry is None and VERSION_KEY_RE.fullmatch(channel):");
    try expectContains(installer, "return target_key, channel, infer_tarball_url(channel, target_key, system_key)");
}

test "installer only permits offline index fallback for explicit versions" {
    try expectContains(installer, "def load_index(channel: str) -> dict:");
    try expectContains(installer, "return read_index()");
    try expectContains(installer, "except urllib.error.HTTPError:");
    try expectContains(installer, "except urllib.error.URLError:");
    try expectContains(installer, "if not is_explicit_version(channel):");
    try expectContains(installer, "raise");
    try expectContains(installer, "return {}");

    try expectContains(installer, "assert resolve_target(");
    try expectContains(installer, "{'0.16.0': sample_index['0.16.0']}");
    try expectContains(installer, "'https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'");
}

test "installer preserves extracted binary layout and resolve-only status output" {
    try expectContains(installer, "bin_dir = final_root");
    try expectContains(installer, "if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():");
    try expectContains(installer, "elif (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
    try expectContains(installer, "could not locate zig binary in {final_root}");

    try expectContains(installer, "parser.add_argument('--resolve-only'");
    try expectContains(installer, "ZIG_INSTALL_CHANNEL={channel}");
    try expectContains(installer, "ZIG_INSTALL_VERSION={version}");
    try expectContains(installer, "ZIG_INSTALL_TARGET={target_key}");
    try expectContains(installer, "ZIG_INSTALL_URL={tarball_url}");
    try expectContains(installer, "ZIG_INSTALL_STATUS=resolved");
}
