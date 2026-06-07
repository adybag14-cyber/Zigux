const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireOrderAfter(haystack: []const u8, anchor: []const u8, earlier: []const u8, later: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    try requireOrder(haystack[anchor_index..], earlier, later);
}

test "cli parser exposes action path and archive controls" {
    try requireContains(installer_source, "parser = argparse.ArgumentParser(description='Install Zig from the official Zig download index or a direct version archive URL.')");
    try requireContains(installer_source, "parser.add_argument('--channel', default=None");
    try requireContains(installer_source, "parser.add_argument('--dest', default='.zig-toolchain'");
    try requireContains(installer_source, "parser.add_argument('--system'");
    try requireContains(installer_source, "parser.add_argument('--arch'");
    try requireContains(installer_source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try requireContains(installer_source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try requireContains(installer_source, "parser.add_argument('--resolve-only', action='store_true'");
    try requireContains(installer_source, "parser.add_argument('--self-test', action='store_true'");
}

test "self-test exits before policy, platform, index, or archive resolution" {
    try requireOrderAfter(
        installer_source,
        "def main() -> int:",
        "if args.self_test:\n        return run_self_test()",
        "policy_channel = load_policy_channel()",
    );
    try requireContains(installer_source, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try requireContains(installer_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}

test "archive target checksum selection is resolved before public output" {
    try requireOrder(installer_source, "archive_target_key = args.archive_target or target_key", "print(f'ZIG_INSTALL_CHANNEL={channel}')");
    try requireOrder(installer_source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:", "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try requireOrder(installer_source, "if args.archive_target is not None:\n        print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')", "if expected_archive_sha256 is not None:\n        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try requireContains(installer_source, "f'no pinned archive sha256 for target {archive_target_key} in {TOOLCHAIN_POLICY}'");
}

test "resolve-only returns before destination creation and staging" {
    try requireOrder(installer_source, "if args.resolve_only:\n        print('ZIG_INSTALL_STATUS=resolved')\n        return 0", "install_root = Path(args.dest)");
    try requireOrder(installer_source, "install_root.mkdir(parents=True, exist_ok=True)", "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try requireOrder(installer_source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
}

test "install path reports source, path publication, and final pass in order" {
    try requireOrder(installer_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try requireOrder(installer_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
    try requireOrder(installer_source, "bin_dir = resolve_bin_dir(final_root)", "append_github_path(bin_dir)");
    try requireOrder(installer_source, "append_github_path(bin_dir)", "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try requireOrder(installer_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')", "print('ZIG_INSTALL_STATUS=pass')");
}
