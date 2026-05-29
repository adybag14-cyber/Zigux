const std = @import("std");

const expect = std.testing.expect;
const expectEqual = std.testing.expectEqual;

const workflow_excerpt =
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
    \\          mirror_file=".zig-toolchain/community-mirrors.txt"
    \\          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\          repo_archive_parts_dir="${repo_archive_path}.parts"
    \\          rm -f "$archive_path" "$mirror_file"
    \\          rm -rf "$extract_root"
    \\          try_local_archive() {
    \\            if [ ! -f "$repo_archive_path" ]; then
    \\              if [ ! -d "$repo_archive_parts_dir" ]; then
    \\                return 1
    \\              fi
    \\              python3 scripts/zigux/stage-pinned-zig-archive.py \
    \\                --root "$GITHUB_WORKSPACE" \
    \\                --parts-dir "$repo_archive_parts_dir" || return 1
    \\            fi
    \\            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\              tar -xJf "$repo_archive_path" -C .zig-toolchain
    \\              zig_path="$extract_root/zig"
    \\              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\                return 0
    \\              fi
    \\            fi
    \\            rm -rf "$extract_root"
    \\            return 1
    \\          }
    \\          try_download() {
    \\            local url="$1"
    \\            if curl -L --fail "$url" -o "$archive_path"; then
    \\              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\                tar -xJf "$archive_path" -C .zig-toolchain
    \\                zig_path="$extract_root/zig"
    \\                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\                  return 0
    \\                fi
    \\              fi
    \\              rm -f "$archive_path"
    \\              rm -rf "$extract_root"
    \\            fi
    \\            return 1
    \\          }
    \\          download_success=0
    \\          if try_local_archive; then
    \\            download_success=1
    \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
    \\              [ -n "$mirror_url" ] || continue
    \\              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\                download_success=1
    \\                break
    \\              fi
    \\            done < "$mirror_file"
    \\          fi
    \\          if [ "$download_success" -ne 1 ]; then
    \\            if try_download "$ZIGUX_ZIG_URL"; then
    \\              download_success=1
    \\            fi
    \\          fi
    \\          if [ "$download_success" -ne 1 ]; then
    \\            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
    \\            exit 1
    \\          fi
;

fn expectContains(haystack: []const u8, needle: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    return index;
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try expectEqual(expected, count);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try expectContains(haystack, earlier);
    const later_index = try expectContains(haystack, later);
    try expect(earlier_index < later_index);
}

test "lane05 bootstrap install ladder keeps local archive ahead of network fallbacks" {
    try expectBefore(
        workflow_excerpt,
        "if try_local_archive; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o",
    );
    try expectBefore(
        workflow_excerpt,
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    );
    try expectBefore(
        workflow_excerpt,
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
        "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
    );
}

test "lane05 bootstrap local archive path rebuilds from parts before validating" {
    try expectBefore(workflow_excerpt, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectBefore(workflow_excerpt, "if [ ! -f \"$repo_archive_path\" ]; then", "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try expectBefore(workflow_excerpt, "if [ ! -d \"$repo_archive_parts_dir\" ]; then", "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectBefore(workflow_excerpt, "--parts-dir \"$repo_archive_parts_dir\" || return 1", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"");
    try expectBefore(workflow_excerpt, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
}

test "lane05 bootstrap retry ladder owns cleanup around each network attempt" {
    try expectCount(workflow_excerpt, "rm -f \"$archive_path\"", 2);
    try expectCount(workflow_excerpt, "rm -rf \"$extract_root\"", 3);
    const download_start = try expectContains(workflow_excerpt, "if curl -L --fail \"$url\" -o \"$archive_path\"; then");
    const retry_body = workflow_excerpt[download_start..];
    try expectBefore(retry_body, "if curl -L --fail \"$url\" -o \"$archive_path\"; then", "rm -f \"$archive_path\"");
    try expectBefore(retry_body, "if curl -L --fail \"$url\" -o \"$archive_path\"; then", "rm -rf \"$extract_root\"");
}

test "lane05 bootstrap contract fails when direct download is moved before mirrors" {
    const direct = "if try_download \"$ZIGUX_ZIG_URL\"; then";
    const mirrors = "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o";
    const direct_index = try expectContains(workflow_excerpt, direct);
    const mirrors_index = try expectContains(workflow_excerpt, mirrors);
    try expect(mirrors_index < direct_index);
}
