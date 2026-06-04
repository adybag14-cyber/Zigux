const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn readInstaller(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        installer_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "install zig exposes local archive target override surface" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try expectContains(source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContains(source, "archive_target_key = args.archive_target or target_key");
    try expectContains(source, "if args.archive_target is not None:");
    try expectContains(source, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");

    try expectOrder(source, "parser.add_argument('--archive'", "parser.add_argument('--archive-target'");
    try expectOrder(source, "archive_target_key = args.archive_target or target_key", "if args.archive_target is not None:");
    try expectOrder(source, "if args.archive_target is not None:", "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
}

test "install zig switches pinned digest checks to explicit archive target" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "if channel == policy_channel:");
    try expectContains(source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)");
    try expectContains(source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContains(source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContains(source, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectContains(source, "f'no pinned archive sha256 for target {archive_target_key} in {TOOLCHAIN_POLICY}'");
    try expectContains(source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContains(source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");

    try expectOrder(source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)", "archive_target_key = args.archive_target or target_key");
    try expectOrder(source, "archive_target_key = args.archive_target or target_key", "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectOrder(source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)", "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectOrder(source, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
}

test "install zig archive target path stays policy only and download free" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContains(source, "local_archive = Path(args.archive).expanduser() if args.archive is not None else None");
    try expectContains(source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectContains(source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");

    try expectOrder(source, "local_archive = Path(args.archive).expanduser() if args.archive is not None else None", "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectOrder(source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectOrder(source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
}
