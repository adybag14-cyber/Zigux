const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "local archive staging validates source path before copy" {
    try requireContains(installer_source, "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:");
    try requireContains(installer_source, "if local_archive is not None:");
    try requireBefore(
        installer_source,
        "if not local_archive.exists():",
        "shutil.copyfile(local_archive, archive_path)",
    );
    try requireBefore(
        installer_source,
        "if not local_archive.is_file():",
        "shutil.copyfile(local_archive, archive_path)",
    );
    try requireContains(installer_source, "raise SystemExit(f'local Zig archive not found: {local_archive}')");
    try requireContains(installer_source, "raise SystemExit(f'local Zig archive is not a regular file: {local_archive}')");
}

test "local archive staging creates destination parent and reports local source" {
    try requireBefore(
        installer_source,
        "archive_path.parent.mkdir(parents=True, exist_ok=True)",
        "shutil.copyfile(local_archive, archive_path)",
    );
    try requireBefore(
        installer_source,
        "shutil.copyfile(local_archive, archive_path)",
        "return 'local_archive'",
    );
    try requireContains(installer_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
}

test "download branch remains separate from local archive copy branch" {
    try requireBefore(
        installer_source,
        "return 'local_archive'",
        "copy_url_to_file(tarball_url, archive_path)",
    );
    try requireBefore(
        installer_source,
        "copy_url_to_file(tarball_url, archive_path)",
        "return 'download'",
    );
}

test "main stages the selected archive name before verification and extraction" {
    try requireContains(installer_source, "local_archive = Path(args.archive).expanduser() if args.archive is not None else None");
    try requireContains(installer_source, "archive_name = local_archive.name if local_archive is not None else tarball_url.rsplit('/', 1)[-1]");
    try requireBefore(
        installer_source,
        "archive_name = local_archive.name if local_archive is not None else tarball_url.rsplit('/', 1)[-1]",
        "archive_path = tmpdir / archive_name",
    );
    try requireBefore(
        installer_source,
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    );
    try requireBefore(
        installer_source,
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    );
}

test "installer self-test keeps local and download staging branches covered" {
    try requireBefore(
        installer_source,
        "local_archive.write_bytes(b'local-zig-archive')",
        "source = stage_archive(local_archive, 'https://example.invalid/archive.tar.xz', staged_archive)",
    );
    try requireBefore(
        installer_source,
        "source = stage_archive(local_archive, 'https://example.invalid/archive.tar.xz', staged_archive)",
        "assert source == 'local_archive'",
    );
    try requireBefore(
        installer_source,
        "assert staged_archive.read_bytes() == b'local-zig-archive'",
        "stage_archive(tmp_root / 'missing.tar.xz', 'https://example.invalid/archive.tar.xz', staged_archive)",
    );
    try requireContains(installer_source, "assert 'local Zig archive not found' in str(exc)");
    try requireBefore(
        installer_source,
        "download_calls: list[tuple[str, Path]] = []",
        "source = stage_archive(None, 'https://example.invalid/archive.tar.xz', staged_archive)",
    );
    try requireBefore(
        installer_source,
        "source = stage_archive(None, 'https://example.invalid/archive.tar.xz', staged_archive)",
        "assert source == 'download'",
    );
    try requireContains(installer_source, "assert download_calls == [('https://example.invalid/archive.tar.xz', staged_archive)]");
}
