const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn readInstaller(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        installer_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOnce(source: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, source[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn requireBefore(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireBeforeAfter(source: []const u8, anchor: []const u8, before: []const u8, after: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, source, anchor) orelse return error.MissingAnchorMarker;
    const tail = source[anchor_index..];
    const before_index = std.mem.indexOf(u8, tail, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, tail, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "install-zig stage_archive keeps local archive validation before copy" {
    const allocator = std.testing.allocator;
    const source = try readInstaller(allocator);
    defer allocator.free(source);

    try requireOnce(
        source,
        "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:",
    );
    try requireContains(source, "if local_archive is not None:");
    try requireContains(source, "if not local_archive.exists():");
    try requireContains(source, "local Zig archive not found");
    try requireContains(source, "if not local_archive.is_file():");
    try requireContains(source, "local Zig archive is not a regular file");
    try requireContains(source, "archive_path.parent.mkdir(parents=True, exist_ok=True)");
    try requireContains(source, "shutil.copyfile(local_archive, archive_path)");
    try requireContains(source, "return 'local_archive'");

    const stage_anchor = "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:";
    try requireBeforeAfter(source, stage_anchor, "if not local_archive.exists():", "shutil.copyfile(local_archive, archive_path)");
    try requireBeforeAfter(source, stage_anchor, "if not local_archive.is_file():", "shutil.copyfile(local_archive, archive_path)");
    try requireBeforeAfter(source, stage_anchor, "shutil.copyfile(local_archive, archive_path)", "return 'local_archive'");
}

test "install-zig stage_archive keeps download staging distinct" {
    const allocator = std.testing.allocator;
    const source = try readInstaller(allocator);
    defer allocator.free(source);

    try requireContains(source, "copy_url_to_file(tarball_url, archive_path)");
    try requireContains(source, "return 'download'");
    const stage_anchor = "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:";
    try requireBeforeAfter(source, stage_anchor, "return 'local_archive'", "copy_url_to_file(tarball_url, archive_path)");
    try requireBeforeAfter(source, stage_anchor, "copy_url_to_file(tarball_url, archive_path)", "return 'download'");
}

test "install-zig main reports archive source before extraction" {
    const allocator = std.testing.allocator;
    const source = try readInstaller(allocator);
    defer allocator.free(source);

    try requireContains(source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try requireContains(source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try requireContains(source, "if args.resolve_only:");
    try requireContains(source, "local_archive = Path(args.archive).expanduser() if args.archive is not None else None");
    try requireContains(source, "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try requireContains(source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try requireContains(source, "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");

    try requireBeforeAfter(source, "def main() -> int:", "if args.resolve_only:", "local_archive = Path(args.archive).expanduser() if args.archive is not None else None");
    try requireBeforeAfter(source, "def main() -> int:", "local_archive = Path(args.archive).expanduser() if args.archive is not None else None", "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try requireBeforeAfter(source, "def main() -> int:", "archive_source = stage_archive(local_archive, tarball_url, archive_path)", "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try requireBeforeAfter(source, "def main() -> int:", "print(f'ZIG_INSTALL_SOURCE={archive_source}')", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
}
