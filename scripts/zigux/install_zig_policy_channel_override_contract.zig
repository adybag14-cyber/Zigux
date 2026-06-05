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

fn expectAppearsExactly(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "policy channel is loaded before CLI channel override resolution" {
    try expectContains(install_zig_text, "def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:");
    try expectContains(install_zig_text, "policy_channel = load_policy_channel()");
    try expectContains(install_zig_text, "channel = args.channel or policy_channel");
    try expectContains(install_zig_text, "index = load_index(channel)");
    try expectContains(install_zig_text, "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)");
    try expectBefore(install_zig_text, "policy_channel = load_policy_channel()", "channel = args.channel or policy_channel");
    try expectBefore(install_zig_text, "channel = args.channel or policy_channel", "index = load_index(channel)");
    try expectBefore(install_zig_text, "index = load_index(channel)", "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)");
    try expectBefore(install_zig_text, "system_key = args.system or normalize_os(platform.system())", "target_key, version, tarball_url = resolve_target");
    try expectBefore(install_zig_text, "arch_key = args.arch or normalize_arch(platform.machine())", "target_key, version, tarball_url = resolve_target");
}

test "archive target override is scoped to policy digest lookup after target resolution" {
    try expectContains(install_zig_text, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContains(install_zig_text, "expected_archive_sha256 = None");
    try expectContains(install_zig_text, "if channel == policy_channel:");
    try expectContains(install_zig_text, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)");
    try expectContains(install_zig_text, "archive_target_key = args.archive_target or target_key");
    try expectContains(install_zig_text, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContains(install_zig_text, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContains(install_zig_text, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectContains(install_zig_text, "no pinned archive sha256 for target {archive_target_key}");
    try expectBefore(install_zig_text, "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)", "archive_target_key = args.archive_target or target_key");
    try expectBefore(install_zig_text, "archive_target_key = args.archive_target or target_key", "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectAppearsExactly(install_zig_text, "resolve_target(index, channel, arch_key, system_key)", 1);
}

test "install action output preserves policy digest and resolve-only ordering" {
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_CHANNEL={channel}')");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_VERSION={version}')");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_TARGET={target_key}')");
    try expectContains(install_zig_text, "if args.archive_target is not None:");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_URL={tarball_url}')");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try expectContains(install_zig_text, "if args.resolve_only:");
    try expectContains(install_zig_text, "print('ZIG_INSTALL_STATUS=resolved')");
    try expectBefore(install_zig_text, "print(f'ZIG_INSTALL_CHANNEL={channel}')", "print(f'ZIG_INSTALL_VERSION={version}')");
    try expectBefore(install_zig_text, "print(f'ZIG_INSTALL_VERSION={version}')", "print(f'ZIG_INSTALL_TARGET={target_key}')");
    try expectBefore(install_zig_text, "print(f'ZIG_INSTALL_TARGET={target_key}')", "print(f'ZIG_INSTALL_URL={tarball_url}')");
    try expectBefore(install_zig_text, "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')", "if args.resolve_only:");
    try expectBefore(install_zig_text, "if args.resolve_only:", "install_root = Path(args.dest)");
}

test "archive staging source is reported only after policy digest verification path" {
    try expectContains(install_zig_text, "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectContains(install_zig_text, "if expected_archive_sha256 is not None:");
    try expectContains(install_zig_text, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')");
    try expectContains(install_zig_text, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectContains(install_zig_text, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')");
    try expectContains(install_zig_text, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectBefore(install_zig_text, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectBefore(install_zig_text, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectBefore(install_zig_text, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectBefore(install_zig_text, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectBefore(install_zig_text, "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
}
