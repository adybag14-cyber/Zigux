const std = @import("std");

const pinned_target = "x86_64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const direct_host = "ziglang.org";

const pinned_filename = "zig-" ++ pinned_target ++ "-" ++ pinned_channel ++ ".tar.xz";
const canonical_url = "https://github.com/" ++ canonical_repo ++ "/releases/download/" ++ canonical_tag ++ "/" ++ pinned_filename;
const direct_url = "https://" ++ direct_host ++ "/builds/" ++ pinned_filename;
const repo_archive_path = "third_party/" ++ pinned_filename;
const repo_archive_parts_path = repo_archive_path ++ ".parts";

const workflow_excerpt =
    \\          canonical_repo = "adybag14-cyber/zig"
    \\          canonical_tag = "upstream-748e7c5e39fc"
    \\          url = f"https://ziglang.org/builds/{filename}"
    \\          canonical_url = f"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}"
    \\          print(f"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'")
    \\          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\          repo_archive_parts_dir="${repo_archive_path}.parts"
    \\          if try_local_archive; then
    \\            download_success=1
    \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\            download_success=1
    \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\          if [ "$download_success" -ne 1 ]; then
    \\            if try_download "$ZIGUX_ZIG_URL"; then
    \\              download_success=1
    \\            fi
    \\          fi
;

const installer_excerpt =
    \\CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'
    \\CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')
    \\CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')
    \\    if channel == CANONICAL_RELEASE_CHANNEL:
    \\        return (
    \\            f'https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/'
    \\            f'{CANONICAL_RELEASE_TAG}/zig-{target_key}-{channel}{suffix}'
    \\        )
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: []const u8 = haystack;
    while (std.mem.indexOf(u8, cursor, needle)) |index| {
        count += 1;
        cursor = cursor[index + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "lane05 canonical release identity stays pinned to the current archive packet" {
    try std.testing.expectEqualStrings("x86_64-linux", pinned_target);
    try std.testing.expectEqualStrings("0.17.0-dev.758+748e7c5e3", pinned_channel);
    try std.testing.expectEqualStrings("0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6", pinned_sha256);
    try std.testing.expectEqualStrings("zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz", pinned_filename);
    try std.testing.expectEqualStrings("third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz", repo_archive_path);
    try std.testing.expectEqualStrings("third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts", repo_archive_parts_path);
    try std.testing.expectEqualStrings(
        "https://github.com/adybag14-cyber/zig/releases/download/upstream-748e7c5e39fc/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        canonical_url,
    );
    try std.testing.expectEqualStrings(
        "https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        direct_url,
    );
}

test "bootstrap workflow keeps canonical release before network mirror fallback" {
    try expectContains(workflow_excerpt, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(workflow_excerpt, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(workflow_excerpt, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(workflow_excerpt, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow_excerpt, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow_excerpt, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow_excerpt, "try_download \"$ZIGUX_ZIG_URL\"");

    try expectBefore(workflow_excerpt, "if try_local_archive; then", "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectBefore(workflow_excerpt, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow_excerpt, "https://ziglang.org/download/community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
    try expectBefore(workflow_excerpt, "canonical_repo = \"adybag14-cyber/zig\"", "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectBefore(workflow_excerpt, "canonical_tag = \"upstream-748e7c5e39fc\"", "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"");
}

test "installer helper keeps local release overrides separate from CI constants" {
    try expectContains(installer_excerpt, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
    try expectContains(installer_excerpt, "ZIGUX_ZIG_RELEASE_REPO");
    try expectContains(installer_excerpt, "ZIGUX_ZIG_RELEASE_TAG");
    try expectContains(installer_excerpt, "'adybag14-cyber/zig'");
    try expectContains(installer_excerpt, "'upstream-748e7c5e39fc'");
    try expectContains(installer_excerpt, "https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/");

    try expectBefore(installer_excerpt, "CANONICAL_RELEASE_CHANNEL", "CANONICAL_RELEASE_REPO");
    try expectBefore(installer_excerpt, "CANONICAL_RELEASE_REPO", "CANONICAL_RELEASE_TAG");
    try expectBefore(installer_excerpt, "if channel == CANONICAL_RELEASE_CHANNEL", "https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/");
}

test "canonical markers are unique enough to catch drift without masking fallbacks" {
    try expectExactCount(workflow_excerpt, "adybag14-cyber/zig", 1);
    try expectExactCount(workflow_excerpt, "upstream-748e7c5e39fc", 1);
    try expectExactCount(workflow_excerpt, "ZIGUX_ZIG_CANONICAL_URL", 2);
    try expectExactCount(installer_excerpt, "ZIGUX_ZIG_RELEASE_REPO", 1);
    try expectExactCount(installer_excerpt, "ZIGUX_ZIG_RELEASE_TAG", 1);
    try expectExactCount(installer_excerpt, "CANONICAL_RELEASE_CHANNEL", 2);
}
