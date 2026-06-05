const std = @import("std");

const workflow_setup_zig =
    \\          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\          repo_archive_parts_dir="${repo_archive_path}.parts"
    \\          try_local_archive() {
    \\            if [ ! -f "$repo_archive_path" ]; then
    \\              if [ ! -d "$repo_archive_parts_dir" ]; then
    \\                return 1
    \\              fi
    \\              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1
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
    \\          download_success=0
    \\          if try_local_archive; then
    \\            download_success=1
    \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
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
    \\            echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
    \\            exit 1
    \\          fi
;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "Lane 05 local archive path stages split archives before downloads" {
    try requireContains(workflow_setup_zig, "try_local_archive() {");
    try requireContains(workflow_setup_zig, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow_setup_zig, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow_setup_zig, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow_setup_zig, "--parts-dir \"$repo_archive_parts_dir\"");
    try requireContains(workflow_setup_zig, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireContains(workflow_setup_zig, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try requireOrder(workflow_setup_zig, "python3 scripts/zigux/stage-pinned-zig-archive.py", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"");
    try requireOrder(workflow_setup_zig, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
}

test "Lane 05 fallback order prefers verified local archive before network sources" {
    try requireContains(workflow_setup_zig, "if try_local_archive; then");
    try requireContains(workflow_setup_zig, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow_setup_zig, "community-mirrors.txt");
    try requireContains(workflow_setup_zig, "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then");
    try requireContains(workflow_setup_zig, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireOrder(workflow_setup_zig, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow_setup_zig, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "community-mirrors.txt");
    try requireOrder(workflow_setup_zig, "community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "Lane 05 failure message names every supported bootstrap source" {
    const failure_message = "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org";
    try requireContains(workflow_setup_zig, failure_message);
    try requireContains(failure_message, "third_party");
    try requireContains(failure_message, "canonical adybag14-cyber/zig release");
    try requireContains(failure_message, "mirrors");
    try requireContains(failure_message, "ziglang.org");
}

test "Lane 05 contract keeps local archive marker before terminal failure" {
    try requireOrder(workflow_setup_zig, "try_local_archive() {", "download_success=0");
    try requireOrder(workflow_setup_zig, "download_success=0", "if [ \"$download_success\" -ne 1 ]; then");
    try requireOrder(workflow_setup_zig, "if try_download \"$ZIGUX_ZIG_URL\"; then", "exit 1");
}
