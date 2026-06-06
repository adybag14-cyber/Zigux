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

fn expectAppearsAtLeast(haystack: []const u8, needle: []const u8, minimum: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expect(count >= minimum);
}

test "installer normalizes supported OS spellings before target resolution" {
    try expectContains(install_zig_text, "def normalize_os(name: str) -> str:");
    try expectContains(install_zig_text, "if lowered.startswith('linux'):");
    try expectContains(install_zig_text, "return 'linux'");
    try expectContains(install_zig_text, "if lowered.startswith('darwin') or lowered.startswith('mac'):");
    try expectContains(install_zig_text, "return 'macos'");
    try expectContains(install_zig_text, "if lowered.startswith('windows'):");
    try expectContains(install_zig_text, "return 'windows'");
    try expectContains(install_zig_text, "unsupported OS for Zig installer");
    try expectContains(install_zig_text, "assert normalize_os('Linux') == 'linux'");
    try expectContains(install_zig_text, "assert normalize_os('Darwin') == 'macos'");
    try expectContains(install_zig_text, "assert normalize_os('Windows') == 'windows'");
    try expectContains(install_zig_text, "normalize_os('plan9')");
    try expectContains(install_zig_text, "expected normalize_os to reject unsupported OS");
}

test "installer normalizes supported CPU aliases and rejects unknown architectures" {
    try expectContains(install_zig_text, "def normalize_arch(name: str) -> str:");
    try expectContains(install_zig_text, "if lowered in {'amd64', 'x86_64', 'x64'}:");
    try expectContains(install_zig_text, "return 'x86_64'");
    try expectContains(install_zig_text, "if lowered in {'arm64', 'aarch64'}:");
    try expectContains(install_zig_text, "return 'aarch64'");
    try expectContains(install_zig_text, "if lowered in {'x86', 'i386', 'i686'}:");
    try expectContains(install_zig_text, "return 'x86'");
    try expectContains(install_zig_text, "unsupported architecture for Zig installer");
    try expectContains(install_zig_text, "assert normalize_arch('amd64') == 'x86_64'");
    try expectContains(install_zig_text, "assert normalize_arch('aarch64') == 'aarch64'");
    try expectContains(install_zig_text, "assert normalize_arch('i686') == 'x86'");
    try expectContains(install_zig_text, "normalize_arch('sparc')");
    try expectContains(install_zig_text, "expected normalize_arch to reject unsupported architecture");
}

test "target key and archive suffix are derived from normalized arch and system" {
    try expectContains(install_zig_text, "target_key = f'{arch_key}-{system_key}'");
    try expectContains(install_zig_text, "suffix = '.zip' if system_key == 'windows' else '.tar.xz'");
    try expectContains(install_zig_text, "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'");
    try expectContains(install_zig_text, "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'");
    try expectBefore(install_zig_text, "target_key = f'{arch_key}-{system_key}'", "entry = index.get(channel)");
    try expectBefore(
        install_zig_text,
        "suffix = '.zip' if system_key == 'windows' else '.tar.xz'",
        "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
    );
    try expectContains(install_zig_text, "if archive_path.suffix == '.zip':");
    try expectContains(install_zig_text, "with zipfile.ZipFile(archive_path) as zf:");
    try expectContains(install_zig_text, "with tarfile.open(archive_path, 'r:*') as tf:");
}

test "canonical release and offline explicit versions infer target archives without index entries" {
    try expectContains(install_zig_text, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
    try expectContains(install_zig_text, "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:");
    try expectContains(install_zig_text, "if channel == CANONICAL_RELEASE_CHANNEL:");
    try expectContains(install_zig_text, "return target_key, channel, infer_tarball_url(channel, target_key, system_key)");
    try expectBefore(
        install_zig_text,
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "entry = index.get(channel)",
    );
    try expectContains(install_zig_text, "if entry is None and VERSION_KEY_RE.fullmatch(channel):");
    try expectContains(install_zig_text, "except (TimeoutError, urllib.error.URLError):");
    try expectContains(install_zig_text, "if not is_explicit_version(channel):");
    try expectContains(install_zig_text, "return {}");
    try expectBefore(
        install_zig_text,
        "index = load_index(channel)",
        "target_key, version, tarball_url = resolve_target",
    );
}

test "CLI target overrides feed the same normalized resolution path" {
    try expectContains(install_zig_text, "parser.add_argument('--system', help='Override detected OS key (linux, macos, windows)')");
    try expectContains(install_zig_text, "parser.add_argument('--arch', help='Override detected architecture key (x86_64, aarch64, x86)')");
    try expectContains(install_zig_text, "system_key = args.system or normalize_os(platform.system())");
    try expectContains(install_zig_text, "arch_key = args.arch or normalize_arch(platform.machine())");
    try expectBefore(install_zig_text, "system_key = args.system or normalize_os(platform.system())", "target_key, version, tarball_url = resolve_target");
    try expectBefore(install_zig_text, "arch_key = args.arch or normalize_arch(platform.machine())", "target_key, version, tarball_url = resolve_target");
    try expectAppearsAtLeast(install_zig_text, "resolve_target(sample_index,", 4);
    try expectContains(install_zig_text, "expected resolve_target to reject unknown target");
}
