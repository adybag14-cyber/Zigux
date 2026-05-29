const std = @import("std");
const testing = std.testing;

const installer_source = @embedFile("install-zig.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn hasMarker(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectAny(haystack: []const u8, comptime needles: []const []const u8) !void {
    inline for (needles) |needle| {
        if (hasMarker(haystack, needle)) return;
    }
    return error.MissingAnyMarker;
}

test "installer accepts exactly one extracted root from tar or zip archives" {
    try expectContains(installer_source, "def extract_archive(archive_path: Path, dest: Path) -> Path:");
    try expectContains(installer_source, "with zipfile.ZipFile(archive_path) as zf:");
    try expectContains(installer_source, "with tarfile.open(archive_path, 'r:*') as tf:");
    try expectContains(installer_source, "children = [child for child in dest.iterdir() if child.is_dir()]");
    try expectContains(installer_source, "if len(children) != 1:");
    try expectContains(installer_source, "unexpected extracted layout in {dest}");
    try expectBefore(installer_source, "if len(children) != 1:", "return children[0]");
}

test "installer resolves both root and bin zig layouts before publishing path" {
    try expectAny(installer_source, &.{
        "def resolve_bin_dir(final_root: Path) -> Path:",
        "bin_dir = final_root",
    });
    try expectContains(installer_source, "if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():");
    try expectAny(installer_source, &.{
        "return final_root",
        "bin_dir = final_root",
    });
    try expectContains(installer_source, "if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
    try expectAny(installer_source, &.{
        "return final_root / 'bin'",
        "bin_dir = final_root / 'bin'",
    });
    try expectContains(installer_source, "could not locate zig binary in {final_root}");
    try expectAny(installer_source, &.{ "zigux_install_zig_layout_", "append_github_path(bin_dir)" });
}

test "installer replaces the final root from extracted archive output" {
    try expectAny(installer_source, &.{
        "archive_name = local_archive.name if local_archive is not None else tarball_url.rsplit('/', 1)[-1]",
        "archive_name = tarball_url.rsplit('/', 1)[-1]",
    });
    try expectAny(installer_source, &.{
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
        "copy_url_to_file(tarball_url, archive_path)",
    });
    try expectContains(installer_source, "extracted_root = extract_archive(archive_path, tmpdir / 'extract')");
    try expectContains(installer_source, "final_root = install_root / extracted_root.name");
    try expectContains(installer_source, "if final_root.exists():");
    try expectContains(installer_source, "shutil.rmtree(final_root)");
    try expectContains(installer_source, "shutil.copytree(extracted_root, final_root)");
    try expectAny(installer_source, &.{
        "bin_dir = resolve_bin_dir(final_root)",
        "bin_dir = final_root",
    });
}

test "installer publishes github path and final pass status after resolving bin dir" {
    try expectContains(installer_source, "def append_github_path(path: Path) -> None:");
    try expectContains(installer_source, "github_path = os.environ.get('GITHUB_PATH')");
    try expectContains(installer_source, "if not github_path:");
    try expectContains(installer_source, "fh.write(str(path.resolve()) + '\\n')");
    try expectAny(installer_source, &.{
        "print(f'ZIG_INSTALL_SOURCE={archive_source}')",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    });
    try expectContains(installer_source, "append_github_path(bin_dir)");
    try expectContains(installer_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try expectContains(installer_source, "print('ZIG_INSTALL_STATUS=pass')");
    try expectAny(installer_source, &.{
        "bin_dir = resolve_bin_dir(final_root)",
        "bin_dir = final_root",
    });
    try expectBefore(installer_source, "append_github_path(bin_dir)", "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try expectBefore(installer_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')", "print('ZIG_INSTALL_STATUS=pass')");
}

test "pinned policy remains the install publication baseline" {
    try expectContains(policy_source, "\"phase\": \"Phase 2\"");
    try expectContains(policy_source, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_source, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_source, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy_source, "\"required_make_routes\": [");
    try expectContains(policy_source, "\"phase2-toolchain\"");
    try expectContains(policy_source, "\"phase2-tools\"");
    try expectContains(policy_source, "\"phase2-kconfig\"");
    try expectContains(policy_source, "\"phase2-cross\"");
    try expectContains(policy_source, "\"phase2-genksyms\"");
    try expectContains(policy_source, "\"phase2-fixdep\"");
    try expectContains(policy_source, "\"phase2-validate\"");
}
