const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_index = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + end_index];
}

test "toolchain setup resolves the pinned policy into exact archive variables" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const setup = try sliceBetween(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");

    try expectContains(setup, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try expectContains(setup, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(setup, "if len(targets) != 1:");
    try expectContains(setup, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(setup, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(setup, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(setup, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(setup, "ZIGUX_ZIG_URL");
    try expectOrdered(setup, "ZIGUX_ZIG_CANONICAL_URL", "mkdir -p .zig-toolchain");
}

test "local archive and staged parts are tried before network fallbacks" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const setup = try sliceBetween(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");

    try expectContains(setup, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(setup, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(setup, "try_local_archive() {");
    try expectContains(setup, "if [ ! -f \"$repo_archive_path\" ]; then");
    try expectContains(setup, "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try expectContains(setup, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(setup, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(setup, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(setup, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectOrdered(setup, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
}

test "fallback ladder checks canonical release, mirrors, then direct ziglang archive" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const setup = try sliceBetween(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");

    try expectContains(setup, "try_download() {");
    try expectContains(setup, "curl -L --fail \"$url\" -o \"$archive_path\"");
    try expectContains(setup, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(setup, "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"");
    try expectContains(setup, "while IFS= read -r mirror_url; do");
    try expectContains(setup, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectContains(setup, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectOrdered(setup, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try expectOrdered(setup, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if [ \"$download_success\" -ne 1 ]; then");
    try expectOrdered(setup, "if [ \"$download_success\" -ne 1 ]; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "failed archive attempts clean transient state and fail with explicit source inventory" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const setup = try sliceBetween(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");

    try expectContains(setup, "rm -f \"$archive_path\" \"$mirror_file\"");
    try expectContains(setup, "rm -rf \"$extract_root\"");
    try expectContains(setup, "rm -f \"$archive_path\"");
    try expectContains(setup, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectContains(setup, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectContains(setup, "\"$zig_path\" version");
    try expectOrdered(setup, "rm -f \"$archive_path\" \"$mirror_file\"", "try_local_archive() {");
    try expectOrdered(setup, "rm -f \"$archive_path\"", "return 1");
    try expectOrdered(setup, "failed to install a verified pinned Zig archive", "exit 1");
    try expectOrdered(setup, "exit 1", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
}
