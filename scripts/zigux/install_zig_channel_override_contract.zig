const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectContainsExactlyOnce(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, marker));
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readInstaller(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, installer_path, allocator, .limited(512 * 1024));
}

test "installer only loads pinned digest for the active policy channel" {
    const installer_text = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(installer_text);

    try expectContainsExactlyOnce(installer_text, "policy_channel = load_policy_channel()");
    try expectContainsExactlyOnce(installer_text, "channel = args.channel or policy_channel");
    try expectContainsExactlyOnce(installer_text, "expected_archive_sha256 = None");
    try expectContainsExactlyOnce(installer_text, "if channel == policy_channel:\n        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)");
    try expectContainsExactlyOnce(installer_text, "if expected_archive_sha256 is not None:\n        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try expectContainsExactlyOnce(installer_text, "else:\n            print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')");

    try expectBefore(installer_text, "policy_channel = load_policy_channel()", "channel = args.channel or policy_channel");
    try expectBefore(installer_text, "expected_archive_sha256 = None", "if channel == policy_channel:");
    try expectBefore(installer_text, "if channel == policy_channel:", "if args.resolve_only:");
    try expectBefore(installer_text, "if args.resolve_only:", "install_root = Path(args.dest)");
}

test "archive target override stays scoped to local archive policy-channel installs" {
    const installer_text = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(installer_text);

    try expectContainsExactlyOnce(installer_text, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContainsExactlyOnce(installer_text, "archive_target_key = args.archive_target or target_key");
    try expectContainsExactlyOnce(installer_text, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContainsExactlyOnce(installer_text, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContainsExactlyOnce(installer_text, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectContainsExactlyOnce(installer_text, "f'no pinned archive sha256 for target {archive_target_key} in {TOOLCHAIN_POLICY}'");
    try expectContainsExactlyOnce(installer_text, "if args.archive_target is not None:\n        print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");

    try expectBefore(installer_text, "archive_target_key = args.archive_target or target_key", "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectBefore(installer_text, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:", "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectBefore(installer_text, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:", "print(f'ZIG_INSTALL_CHANNEL={channel}')");
}

test "policy-channel digest verification remains before archive extraction" {
    const installer_text = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(installer_text);

    try expectContainsExactlyOnce(installer_text, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContainsExactlyOnce(installer_text, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')");
    try expectContainsExactlyOnce(installer_text, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectContainsExactlyOnce(installer_text, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectContainsExactlyOnce(installer_text, "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");

    try expectBefore(installer_text, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectBefore(installer_text, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectBefore(installer_text, "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
}
