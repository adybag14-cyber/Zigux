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

test "install-zig exposes a resolve-only action path" {
    try requireContains(
        install_zig_source,
        "parser.add_argument('--resolve-only', action='store_true'",
    );
    try requireContains(
        install_zig_source,
        "help='Resolve and print the chosen archive without downloading'",
    );
    try requireContains(
        install_zig_source,
        "if args.resolve_only:\n        print('ZIG_INSTALL_STATUS=resolved')\n        return 0",
    );
}

test "resolve-only reports resolved metadata before returning" {
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_CHANNEL={channel}')",
        "if args.resolve_only:",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_VERSION={version}')",
        "if args.resolve_only:",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_TARGET={target_key}')",
        "if args.resolve_only:",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_URL={tarball_url}')",
        "if args.resolve_only:",
    );
}

test "resolve-only stays before installer side effects" {
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "install_root = Path(args.dest)",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "append_github_path(bin_dir)",
    );
}

test "archive-target metadata is still visible on resolve-only runs" {
    try requireOrder(
        install_zig_source,
        "archive_target_key = args.archive_target or target_key",
        "if args.resolve_only:",
    );
    try requireOrder(
        install_zig_source,
        "if args.archive_target is not None:\n        print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')",
        "if args.resolve_only:",
    );
    try requireOrder(
        install_zig_source,
        "if expected_archive_sha256 is not None:\n        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
        "if args.resolve_only:",
    );
}
