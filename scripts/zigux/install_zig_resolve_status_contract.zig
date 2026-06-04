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

test "resolve-only CLI surface stays explicit" {
    try requireContains(
        install_zig_source,
        "parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')",
    );
    try requireContains(
        install_zig_source,
        "parser.add_argument('--dest', default='.zig-toolchain', help='Install root directory')",
    );
}

test "resolve-only status is emitted after resolved archive metadata" {
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_CHANNEL={channel}')",
        "print(f'ZIG_INSTALL_VERSION={version}')",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_VERSION={version}')",
        "print(f'ZIG_INSTALL_TARGET={target_key}')",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_TARGET={target_key}')",
        "print(f'ZIG_INSTALL_URL={tarball_url}')",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_URL={tarball_url}')",
        "if args.resolve_only:",
    );
    try requireContains(
        install_zig_source,
        "if args.resolve_only:\n        print('ZIG_INSTALL_STATUS=resolved')\n        return 0",
    );
}

test "expected digest remains visible before resolve-only exit" {
    try requireOrder(
        install_zig_source,
        "if expected_archive_sha256 is not None:\n        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
        "if args.resolve_only:",
    );
}

test "resolve-only exits before installation side effects" {
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "install_root = Path(args.dest)",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "install_root.mkdir(parents=True, exist_ok=True)",
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

test "resolve-only path stays separate from install-result status fields" {
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "print('ZIG_INSTALL_STATUS=pass')",
    );
}
