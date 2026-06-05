const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
    DuplicateMarker,
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn requireContains(content: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, content, marker) == null) return ContractError.MissingMarker;
}

fn requireUnique(content: []const u8, marker: []const u8) !void {
    const first = std.mem.indexOf(u8, content, marker) orelse return ContractError.MissingMarker;
    const tail = content[first + marker.len ..];
    if (std.mem.indexOf(u8, tail, marker) != null) return ContractError.DuplicateMarker;
}

fn requireOrdered(content: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, content, cursor, marker) orelse return ContractError.MissingMarker;
        if (found < cursor) return ContractError.MarkerOutOfOrder;
        cursor = found + marker.len;
    }
}

test "setup ladder derives archive names from the pinned policy packet" {
    const content = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(content);

    try requireOrdered(content, &.{
        "name: Setup pinned Zig toolchain",
        "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
        "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
        "if len(targets) != 1:",
        "filename = f\"zig-{target}-{channel}.tar.xz\"",
        "canonical_repo = \"adybag14-cyber/zig\"",
        "canonical_tag = \"upstream-748e7c5e39fc\"",
        "ZIGUX_ZIG_CANONICAL_URL",
        "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
        "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    });

    try requireUnique(content, "canonical_repo = \"adybag14-cyber/zig\"");
    try requireUnique(content, "canonical_tag = \"upstream-748e7c5e39fc\"");
}

test "local archive route stages parts before archive verification and extraction" {
    const content = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(content);

    try requireOrdered(content, &.{
        "try_local_archive() {",
        "if [ ! -f \"$repo_archive_path\" ]; then",
        "if [ ! -d \"$repo_archive_parts_dir\" ]; then",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "--parts-dir \"$repo_archive_parts_dir\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
        "rm -rf \"$extract_root\"",
    });
}

test "download ladder keeps local archive, canonical release, mirrors, then direct ziglang fallback" {
    const content = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(content);

    try requireOrdered(content, &.{
        "download_success=0",
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "while IFS= read -r mirror_url; do",
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"",
        "if [ \"$download_success\" -ne 1 ]; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    });

    try requireContains(content, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
}

test "verified install publishes the extracted Zig path after final success" {
    const content = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(content);

    try requireOrdered(content, &.{
        "if [ \"$download_success\" -ne 1 ]; then",
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
        "exit 1",
        "zig_path=\"$extract_root/zig\"",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
        "\"$zig_path\" version",
    });
}
