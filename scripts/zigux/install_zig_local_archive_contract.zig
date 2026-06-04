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

fn requireSequence(source: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, source[offset..], needle) orelse return error.MissingSequenceMarker;
        offset += relative + needle.len;
    }
}

test "install-zig exposes a local archive install action path" {
    try requireContains(
        install_zig_source,
        "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')",
    );
    try requireContains(
        install_zig_source,
        "local_archive = Path(args.archive).expanduser() if args.archive is not None else None",
    );
    try requireContains(
        install_zig_source,
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
    );
    try requireContains(
        install_zig_source,
        "print(f'ZIG_INSTALL_SOURCE={archive_source}')",
    );
}

test "local archive staging validates the supplied archive before install" {
    try requireContains(
        install_zig_source,
        "if not local_archive.exists():\n            raise SystemExit(f'local Zig archive not found: {local_archive}')",
    );
    try requireContains(
        install_zig_source,
        "if not local_archive.is_file():\n            raise SystemExit(f'local Zig archive is not a regular file: {local_archive}')",
    );
    try requireContains(
        install_zig_source,
        "shutil.copyfile(local_archive, archive_path)\n        return 'local_archive'",
    );
}

test "local archive install verifies pinned sha before extraction" {
    try requireSequence(install_zig_source, &.{
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
        "if expected_archive_sha256 is not None:",
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        "print(f'ZIG_INSTALL_SOURCE={archive_source}')",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    });
}

test "local archive install mutates GitHub path only after extraction copy" {
    try requireSequence(install_zig_source, &.{
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "shutil.copytree(extracted_root, final_root)",
        "bin_dir = resolve_bin_dir(final_root)",
        "append_github_path(bin_dir)",
        "print('ZIG_INSTALL_STATUS=pass')",
    });
}
