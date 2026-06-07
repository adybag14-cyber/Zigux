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

test "extract archive handles zip and tar payloads through one layout gate" {
    try expectContains(installer_source, "import tarfile");
    try expectContains(installer_source, "import zipfile");
    try expectContains(installer_source, "def extract_archive(archive_path: Path, dest: Path) -> Path:");
    try expectContains(installer_source, "if archive_path.suffix == '.zip':");
    try expectContains(installer_source, "with zipfile.ZipFile(archive_path) as zf:");
    try expectContains(installer_source, "zf.extractall(dest)");
    try expectContains(installer_source, "with tarfile.open(archive_path, 'r:*') as tf:");
    try expectContains(installer_source, "tf.extractall(dest)");
}

test "extracted layout must collapse to exactly one directory" {
    try expectContains(installer_source, "children = [child for child in dest.iterdir() if child.is_dir()]");
    try expectContains(installer_source, "if len(children) != 1:");
    try expectContains(installer_source, "raise SystemExit(f'unexpected extracted layout in {dest}')");
    try expectContains(installer_source, "return children[0]");
    try expectOrder(
        installer_source,
        "children = [child for child in dest.iterdir() if child.is_dir()]",
        "return children[0]",
    );
}

test "main install path verifies then extracts then replaces final root" {
    try expectOrder(
        installer_source,
        "verify_archive_sha256(archive_path, expected_archive_sha256)",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    );
    try expectOrder(
        installer_source,
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "final_root = install_root / extracted_root.name",
    );
    try expectOrder(
        installer_source,
        "final_root = install_root / extracted_root.name",
        "if final_root.exists():",
    );
    try expectOrder(installer_source, "if final_root.exists():", "shutil.rmtree(final_root)");
    try expectOrder(installer_source, "shutil.rmtree(final_root)", "shutil.copytree(extracted_root, final_root)");
}

test "binary directory resolution remains after extraction publication" {
    if (std.mem.indexOf(u8, installer_source, "def resolve_bin_dir(final_root: Path) -> Path:") != null) {
        try expectContains(installer_source, "def resolve_bin_dir(final_root: Path) -> Path:");
        try expectContains(installer_source, "if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():");
        try expectContains(installer_source, "if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
        try expectContains(installer_source, "raise SystemExit(f'could not locate zig binary in {final_root}')");
        try expectOrder(
            installer_source,
            "shutil.copytree(extracted_root, final_root)",
            "bin_dir = resolve_bin_dir(final_root)",
        );
    } else {
        try expectContains(installer_source, "bin_dir = final_root");
        try expectContains(installer_source, "elif (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
        try expectContains(installer_source, "raise SystemExit(f'could not locate zig binary in {final_root}')");
        try expectOrder(installer_source, "shutil.copytree(extracted_root, final_root)", "bin_dir = final_root");
    }

    try expectOrder(installer_source, "bin_dir", "append_github_path(bin_dir)");
    try expectOrder(installer_source, "append_github_path(bin_dir)", "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try expectOrder(installer_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')", "print('ZIG_INSTALL_STATUS=pass')");
}
