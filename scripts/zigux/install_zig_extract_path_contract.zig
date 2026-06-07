const std = @import("std");
const testing = std.testing;

const installer_source = @embedFile("install-zig.py");

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, installer_source, needle) != null);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, installer_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, installer_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "extract archive accepts zip and tar while requiring one top-level directory" {
    try requireContains("def extract_archive(archive_path: Path, dest: Path) -> Path:");
    try requireContains("if archive_path.suffix == '.zip':");
    try requireContains("with zipfile.ZipFile(archive_path) as zf:");
    try requireContains("zf.extractall(dest)");
    try requireContains("with tarfile.open(archive_path, 'r:*') as tf:");
    try requireContains("tf.extractall(dest)");
    try requireContains("children = [child for child in dest.iterdir() if child.is_dir()]");
    try requireContains("if len(children) != 1:");
    try requireContains("unexpected extracted layout in {dest}");
    try requireContains("return children[0]");

    try requireOrder("with zipfile.ZipFile(archive_path) as zf:", "zf.extractall(dest)");
    try requireOrder("with tarfile.open(archive_path, 'r:*') as tf:", "tf.extractall(dest)");
    try requireOrder("children = [child for child in dest.iterdir() if child.is_dir()]", "return children[0]");
}

test "bin directory resolution accepts root or bin zig executables" {
    try requireContains("def resolve_bin_dir(final_root: Path) -> Path:");
    try requireContains("if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():");
    try requireContains("return final_root");
    try requireContains("if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
    try requireContains("return final_root / 'bin'");
    try requireContains("could not locate zig binary in {final_root}");

    try requireOrder("if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():", "if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
    try requireOrder("if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():", "could not locate zig binary in {final_root}");
}

test "stage archive copies trusted local files before download fallback" {
    try requireContains("def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:");
    try requireContains("if local_archive is not None:");
    try requireContains("if not local_archive.exists():");
    try requireContains("local Zig archive not found: {local_archive}");
    try requireContains("if not local_archive.is_file():");
    try requireContains("local Zig archive is not a regular file: {local_archive}");
    try requireContains("archive_path.parent.mkdir(parents=True, exist_ok=True)");
    try requireContains("shutil.copyfile(local_archive, archive_path)");
    try requireContains("return 'local_archive'");
    try requireContains("copy_url_to_file(tarball_url, archive_path)");
    try requireContains("return 'download'");

    try requireOrder("if local_archive is not None:", "shutil.copyfile(local_archive, archive_path)");
    try requireOrder("return 'local_archive'", "copy_url_to_file(tarball_url, archive_path)");
    try requireOrder("copy_url_to_file(tarball_url, archive_path)", "return 'download'");
}

test "github path handoff appends the resolved directory with newline discipline" {
    try requireContains("def append_github_path(path: Path) -> None:");
    try requireContains("github_path = os.environ.get('GITHUB_PATH')");
    try requireContains("if not github_path:");
    try requireContains("return");
    try requireContains("with open(github_path, 'a', encoding='utf-8', newline='\\n') as fh:");
    try requireContains("fh.write(str(path.resolve()) + '\\n')");

    try requireOrder("github_path = os.environ.get('GITHUB_PATH')", "with open(github_path, 'a', encoding='utf-8', newline='\\n') as fh:");
    try requireOrder("with open(github_path, 'a', encoding='utf-8', newline='\\n') as fh:", "fh.write(str(path.resolve()) + '\\n')");
}
