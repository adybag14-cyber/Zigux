const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "install-zig keeps OS aliases narrow and explicit" {
    try requireContains(
        install_zig_source,
        "def normalize_os(name: str) -> str:",
    );
    try requireContains(
        install_zig_source,
        "if lowered.startswith('linux'):\n        return 'linux'",
    );
    try requireContains(
        install_zig_source,
        "if lowered.startswith('darwin') or lowered.startswith('mac'):\n        return 'macos'",
    );
    try requireContains(
        install_zig_source,
        "if lowered.startswith('windows'):\n        return 'windows'",
    );
    try requireContains(
        install_zig_source,
        "raise SystemExit(f'unsupported OS for Zig installer: {name}')",
    );
}

test "install-zig keeps architecture aliases narrow and explicit" {
    try requireContains(
        install_zig_source,
        "def normalize_arch(name: str) -> str:",
    );
    try requireContains(
        install_zig_source,
        "if lowered in {'amd64', 'x86_64', 'x64'}:\n        return 'x86_64'",
    );
    try requireContains(
        install_zig_source,
        "if lowered in {'arm64', 'aarch64'}:\n        return 'aarch64'",
    );
    try requireContains(
        install_zig_source,
        "if lowered in {'x86', 'i386', 'i686'}:\n        return 'x86'",
    );
    try requireContains(
        install_zig_source,
        "raise SystemExit(f'unsupported architecture for Zig installer: {name}')",
    );
}

test "self-test covers representative platform aliases and rejects unknowns" {
    try requireContains(install_zig_source, "assert normalize_os('Linux') == 'linux'");
    try requireContains(install_zig_source, "assert normalize_os('Darwin') == 'macos'");
    try requireContains(install_zig_source, "assert normalize_os('Windows') == 'windows'");
    try requireContains(install_zig_source, "assert normalize_arch('amd64') == 'x86_64'");
    try requireContains(install_zig_source, "assert normalize_arch('aarch64') == 'aarch64'");
    try requireContains(install_zig_source, "assert normalize_arch('i686') == 'x86'");
    try requireContains(install_zig_source, "normalize_os('plan9')");
    try requireContains(install_zig_source, "normalize_arch('sparc')");
    try requireContains(install_zig_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}

test "platform detection runs before index resolution" {
    try requireOrder(
        install_zig_source,
        "system_key = args.system or normalize_os(platform.system())",
        "index = load_index(channel)",
    );
    try requireOrder(
        install_zig_source,
        "arch_key = args.arch or normalize_arch(platform.machine())",
        "index = load_index(channel)",
    );
    try requireOrder(
        install_zig_source,
        "index = load_index(channel)",
        "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)",
    );
}
