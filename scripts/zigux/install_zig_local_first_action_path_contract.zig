const std = @import("std");

const allocator = std.testing.allocator;

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireMarker(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    if (first_index >= second_index) {
        return error.MarkerOrderChanged;
    }
}

test "workflow tries repo-local archive and staged parts before network fallbacks" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try requireMarker(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireMarker(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireMarker(workflow, "if [ ! -f \"$repo_archive_path\" ]; then");
    try requireMarker(workflow, "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try requireMarker(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireMarker(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try requireOrdered(
        workflow,
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    );
}

test "workflow fallback order keeps canonical release before mirrors and direct ziglang" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try requireMarker(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try requireMarker(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try requireMarker(workflow, "ZIGUX_ZIG_CANONICAL_URL");
    try requireMarker(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try requireMarker(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try requireOrdered(
        workflow,
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    );
    try requireOrdered(
        workflow,
        "community-mirrors.txt",
        "try_download \"$ZIGUX_ZIG_URL\"",
    );
}

test "policy and third party note agree on the current pinned archive identity" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const readme = try readRepoFile("third_party/README.md");
    defer allocator.free(readme);

    try requireMarker(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireMarker(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try requireMarker(readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try requireMarker(readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts");
    try requireMarker(readme, "If the repo-local archive is unavailable");
    try requireMarker(readme, "canonical `adybag14-cyber/zig` release before `community-mirrors.txt`");
}
