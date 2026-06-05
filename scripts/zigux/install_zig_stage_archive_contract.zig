const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectOrderAfter(haystack: []const u8, anchor: []const u8, earlier: []const u8, later: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    try expectOrder(haystack[anchor_index..], earlier, later);
}

test "installer exposes explicit local archive and archive target CLI path" {
    try expectContains(installer_source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try expectContains(installer_source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try expectContains(installer_source, "local_archive = Path(args.archive).expanduser() if args.archive is not None else None");
    try expectContains(installer_source, "archive_target_key = args.archive_target or target_key");
    try expectContains(installer_source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try expectContains(installer_source, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try expectContains(installer_source, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
}

test "stage_archive copies local archive before download fallback" {
    try expectContains(installer_source, "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:");
    try expectContains(installer_source, "if local_archive is not None:");
    try expectContains(installer_source, "if not local_archive.exists():");
    try expectContains(installer_source, "raise SystemExit(f'local Zig archive not found: {local_archive}')");
    try expectContains(installer_source, "if not local_archive.is_file():");
    try expectContains(installer_source, "raise SystemExit(f'local Zig archive is not a regular file: {local_archive}')");
    try expectContains(installer_source, "shutil.copyfile(local_archive, archive_path)");
    try expectContains(installer_source, "return 'local_archive'");
    try expectContains(installer_source, "copy_url_to_file(tarball_url, archive_path)");
    try expectContains(installer_source, "return 'download'");
    try expectOrderAfter(
        installer_source,
        "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:",
        "shutil.copyfile(local_archive, archive_path)",
        "copy_url_to_file(tarball_url, archive_path)",
    );
}

test "archive verification happens after staging and before extraction" {
    try expectContains(installer_source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectContains(installer_source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectContains(installer_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try expectContains(installer_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')");
    try expectContains(installer_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectContains(installer_source, "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
    try expectContains(installer_source, "shutil.copytree(extracted_root, final_root)");
    try expectOrder(installer_source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try expectOrder(installer_source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try expectOrder(installer_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
}

test "self-test covers local archive staging and download staging source labels" {
    try expectContains(installer_source, "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_archive_stage_') as tmp_dir:");
    try expectContains(installer_source, "source = stage_archive(local_archive, 'https://example.invalid/archive.tar.xz', staged_archive)");
    try expectContains(installer_source, "assert source == 'local_archive'");
    try expectContains(installer_source, "assert staged_archive.read_bytes() == b'local-zig-archive'");
    try expectContains(installer_source, "assert 'local Zig archive not found' in str(exc)");
    try expectContains(installer_source, "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_download_stage_') as tmp_dir:");
    try expectContains(installer_source, "assert source == 'download'");
    try expectContains(installer_source, "assert download_calls == [('https://example.invalid/archive.tar.xz', staged_archive)]");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}
