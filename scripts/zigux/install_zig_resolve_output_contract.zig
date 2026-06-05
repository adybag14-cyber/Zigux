const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "resolve-only output remains complete before install side effects" {
    try expectContains(install_zig_source, "parser.add_argument('--resolve-only', action='store_true'");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_CHANNEL={channel}')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_VERSION={version}')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_TARGET={target_key}')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_URL={tarball_url}')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try expectContains(install_zig_source, "print('ZIG_INSTALL_STATUS=resolved')");

    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_CHANNEL={channel}')", "print(f'ZIG_INSTALL_VERSION={version}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_VERSION={version}')", "print(f'ZIG_INSTALL_TARGET={target_key}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_TARGET={target_key}')", "print(f'ZIG_INSTALL_URL={tarball_url}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_URL={tarball_url}')", "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')", "print('ZIG_INSTALL_STATUS=resolved')");
    try expectOrdered(install_zig_source, "print('ZIG_INSTALL_STATUS=resolved')", "install_root = Path(args.dest)");
}

test "archive-target override path reports the selected pinned target" {
    try expectContains(install_zig_source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try expectContains(install_zig_source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContains(install_zig_source, "archive_target_key = args.archive_target or target_key");
    try expectContains(install_zig_source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContains(install_zig_source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContains(install_zig_source, "f'no pinned archive sha256 for target {archive_target_key} in {TOOLCHAIN_POLICY}'");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");

    try expectOrdered(install_zig_source, "archive_target_key = args.archive_target or target_key", "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectOrdered(install_zig_source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:", "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_TARGET={target_key}')", "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')", "print(f'ZIG_INSTALL_URL={tarball_url}')");
}

test "verified install output keeps source and final status ordered" {
    try expectContains(install_zig_source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectContains(install_zig_source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')");
    try expectContains(install_zig_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectContains(install_zig_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectContains(install_zig_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try expectContains(install_zig_source, "print('ZIG_INSTALL_STATUS=pass')");

    try expectOrdered(install_zig_source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')", "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectOrdered(install_zig_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
    try expectOrdered(install_zig_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')", "print('ZIG_INSTALL_STATUS=pass')");
}

test "policy values match the resolve output contract" {
    try expectContains(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy_source, "\"archive_target_scope\": [");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\"");
}
