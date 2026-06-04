const std = @import("std");
const testing = std.testing;

const installer = @embedFile("install-zig.py");

fn findAfter(haystack: []const u8, needle: []const u8, start: usize) !usize {
    const offset = std.mem.indexOf(u8, haystack[start..], needle) orelse {
        std.debug.print("missing marker after {d}: {s}\n", .{ start, needle });
        return error.MissingMarker;
    };
    return start + offset;
}

fn requireMarker(needle: []const u8) !usize {
    return findAfter(installer, needle, 0);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_pos = try requireMarker(first);
    const second_pos = try findAfter(installer, second, first_pos + first.len);
    try testing.expect(second_pos > first_pos);
}

fn requireChain(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        cursor = try findAfter(installer, marker, cursor);
        cursor += marker.len;
    }
}

test "archive extraction keeps zip and tar branches plus single-root guard" {
    try requireChain(&.{
        "def extract_archive(archive_path: Path, dest: Path) -> Path:",
        "if archive_path.suffix == '.zip':",
        "with zipfile.ZipFile(archive_path) as zf:",
        "zf.extractall(dest)",
        "else:",
        "with tarfile.open(archive_path, 'r:*') as tf:",
        "tf.extractall(dest)",
        "children = [child for child in dest.iterdir() if child.is_dir()]",
        "if len(children) != 1:",
        "raise SystemExit(f'unexpected extracted layout in {dest}')",
        "return children[0]",
    });
}

test "resolved binary layout accepts root-level and bin-level zig executables" {
    try requireChain(&.{
        "def resolve_bin_dir(final_root: Path) -> Path:",
        "if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():",
        "return final_root",
        "if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():",
        "return final_root / 'bin'",
        "raise SystemExit(f'could not locate zig binary in {final_root}')",
    });
}

test "install flow replaces stale final root before PATH publication" {
    try requireChain(&.{
        "if args.resolve_only:",
        "print('ZIG_INSTALL_STATUS=resolved')",
        "return 0",
        "install_root = Path(args.dest)",
        "install_root.mkdir(parents=True, exist_ok=True)",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "final_root = install_root / extracted_root.name",
        "if final_root.exists():",
        "shutil.rmtree(final_root)",
        "shutil.copytree(extracted_root, final_root)",
        "bin_dir = resolve_bin_dir(final_root)",
        "append_github_path(bin_dir)",
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
        "print('ZIG_INSTALL_STATUS=pass')",
    });
}

test "final layout publication stays after verification and source reporting" {
    try requireOrder(
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    );
    try requireOrder(
        "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
        "print(f'ZIG_INSTALL_SOURCE={archive_source}')",
    );
    try requireOrder(
        "print(f'ZIG_INSTALL_SOURCE={archive_source}')",
        "append_github_path(bin_dir)",
    );
}
