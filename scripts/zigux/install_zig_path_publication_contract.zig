const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectOrdered(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse {
        return error.MissingEarlierMarker;
    };
    const later_index = std.mem.indexOf(u8, source, later) orelse {
        return error.MissingLaterMarker;
    };
    try std.testing.expect(earlier_index < later_index);
}

test "install-zig keeps path publication behind extracted layout resolution" {
    try expectContains(installer_source, "def resolve_bin_dir(final_root: Path) -> Path:");
    try expectContains(installer_source, "if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():");
    try expectContains(installer_source, "return final_root");
    try expectContains(installer_source, "if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():");
    try expectContains(installer_source, "return final_root / 'bin'");
    try expectContains(installer_source, "raise SystemExit(f'could not locate zig binary in {final_root}')");

    try expectOrdered(
        installer_source,
        "def resolve_bin_dir(final_root: Path) -> Path:",
        "def append_github_path(path: Path) -> None:",
    );
    try expectOrdered(
        installer_source,
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "bin_dir = resolve_bin_dir(final_root)",
    );
}

test "install-zig appends resolved bin directory to GitHub action path" {
    try expectContains(installer_source, "github_path = os.environ.get('GITHUB_PATH')");
    try expectContains(installer_source, "if not github_path:");
    try expectContains(installer_source, "return");
    try expectContains(installer_source, "with open(github_path, 'a', encoding='utf-8', newline='\\n') as fh:");
    try expectContains(installer_source, "fh.write(str(path.resolve()) + '\\n')");

    try expectOrdered(
        installer_source,
        "bin_dir = resolve_bin_dir(final_root)",
        "append_github_path(bin_dir)",
    );
}

test "install-zig reports published path before final pass status" {
    try expectContains(installer_source, "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')");
    try expectContains(installer_source, "print('ZIG_INSTALL_STATUS=pass')");
    try expectOrdered(
        installer_source,
        "append_github_path(bin_dir)",
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
    );
    try expectOrdered(
        installer_source,
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
        "print('ZIG_INSTALL_STATUS=pass')",
    );
}
