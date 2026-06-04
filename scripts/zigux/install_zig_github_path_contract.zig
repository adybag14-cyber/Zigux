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

test "install-zig keeps GitHub PATH publication optional and newline delimited" {
    try requireContains(
        install_zig_source,
        "def append_github_path(path: Path) -> None:",
    );
    try requireContains(
        install_zig_source,
        "github_path = os.environ.get('GITHUB_PATH')",
    );
    try requireContains(
        install_zig_source,
        "if not github_path:\n        return",
    );
    try requireContains(
        install_zig_source,
        "with open(github_path, 'a', encoding='utf-8', newline='\\n') as fh:",
    );
    try requireContains(
        install_zig_source,
        "fh.write(str(path.resolve()) + '\\n')",
    );
}

test "installer publishes the resolved bin directory before final status" {
    try requireOrder(
        install_zig_source,
        "append_github_path(bin_dir)",
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
    );
    try requireOrder(
        install_zig_source,
        "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
        "print('ZIG_INSTALL_STATUS=pass')",
    );
}

test "GitHub PATH publication happens after archive extraction and copy" {
    try requireOrder(
        install_zig_source,
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "append_github_path(bin_dir)",
    );
    try requireOrder(
        install_zig_source,
        "shutil.copytree(extracted_root, final_root)",
        "append_github_path(bin_dir)",
    );
}

test "resolve-only returns before GitHub PATH side effects" {
    try requireContains(
        install_zig_source,
        "if args.resolve_only:\n        print('ZIG_INSTALL_STATUS=resolved')\n        return 0",
    );
    try requireOrder(
        install_zig_source,
        "if args.resolve_only:",
        "append_github_path(bin_dir)",
    );
}
