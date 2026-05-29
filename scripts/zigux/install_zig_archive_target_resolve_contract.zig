const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, installer_source, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, installer_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, installer_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "archive target override selects the policy digest for that target" {
    try expectContains("parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContains("archive_target_key = args.archive_target or target_key");
    try expectOrdered(
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:",
    );
    try expectContains("expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectContains("f'no pinned archive sha256 for target {archive_target_key} in {TOOLCHAIN_POLICY}'");
}

test "resolve output reports explicit archive target and pinned digest" {
    try expectOrdered(
        "archive_target_key = args.archive_target or target_key",
        "print(f'ZIG_INSTALL_TARGET={target_key}')",
    );
    try expectContains("if args.archive_target is not None:\n    print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
    try expectOrdered(
        "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')",
        "if expected_archive_sha256 is not None:",
    );
    try expectContains("print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try expectOrdered(
        "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
        "if args.resolve_only:",
    );
}

test "resolve only returns before archive staging or install publication" {
    try expectOrdered(
        "if args.resolve_only:\n    print('ZIG_INSTALL_STATUS=resolved')",
        "install_root = Path(args.dest)",
    );
    try expectOrdered(
        "print('ZIG_INSTALL_STATUS=resolved')\n    return 0",
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
    );
    try expectOrdered(
        "print('ZIG_INSTALL_STATUS=resolved')\n    return 0",
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
    );
}
