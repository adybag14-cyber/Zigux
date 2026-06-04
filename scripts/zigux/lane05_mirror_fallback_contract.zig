const std = @import("std");
const testing = std.testing;

const pinned_target = "x86_64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const mirror_index_url = "https://ziglang.org/download/community-mirrors.txt";
const direct_builds_url = "https://ziglang.org/builds/";
const mirror_bootstrap_query = "?source=github-zigux-bootstrap";

const policy =
    \\"channel": "0.17.0-dev.758+748e7c5e3",
    \\"archive_sha256": {
    \\  "x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
    \\},
    \\"archive_target_scope": [
    \\  "x86_64-linux"
    \\]
;

const third_party_readme =
    \\- target: `x86_64-linux`
    \\- channel: `0.17.0-dev.758+748e7c5e3`
    \\- file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`
    \\- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`
    \\- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL.
    \\- Before retrying the canonical release, mirror, or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
    \\- duplicate-suffix archives are rejected before staging
;

const workflow =
    \\filename = f"zig-{target}-{channel}.tar.xz"
    \\canonical_repo = "adybag14-cyber/zig"
    \\canonical_tag = "upstream-748e7c5e39fc"
    \\url = f"https://ziglang.org/builds/{filename}"
    \\canonical_url = f"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}"
    \\mirror_file=".zig-toolchain/community-mirrors.txt"
    \\rm -f "$archive_path" "$mirror_file"
    \\rm -rf "$extract_root"
    \\try_local_archive() {
    \\  :
    \\}
    \\try_download() {
    \\  :
    \\  rm -f "$archive_path"
    \\  rm -rf "$extract_root"
    \\}
    \\download_success=0
    \\if try_local_archive; then
    \\  download_success=1
    \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\  download_success=1
    \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\  while IFS= read -r mirror_url; do
    \\    [ -n "$mirror_url" ] || continue
    \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\      download_success=1
    \\      break
    \\    fi
    \\  done < "$mirror_file"
    \\fi
    \\if [ "$download_success" -ne 1 ]; then
    \\  if try_download "$ZIGUX_ZIG_URL"; then
    \\    download_success=1
    \\  fi
    \\fi
    \\failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try testing.expect(first != null);

    const rest_start = first.? + needle.len;
    try testing.expect(std.mem.indexOf(u8, haystack[rest_start..], needle) == null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before);
    const after_index = std.mem.indexOf(u8, haystack, after);
    try testing.expect(before_index != null);
    try testing.expect(after_index != null);
    try testing.expect(before_index.? < after_index.?);
}

test "lane05 mirror fallback contract keeps current pin surfaces aligned" {
    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_digest ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\"");

    try expectContains(third_party_readme, "- target: `" ++ pinned_target ++ "`");
    try expectContains(third_party_readme, "- channel: `" ++ pinned_channel ++ "`");
    try expectContains(third_party_readme, "- file: `third_party/" ++ pinned_filename ++ "`");
    try expectContains(third_party_readme, "- sha256: `" ++ pinned_digest ++ "`");

    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try expectContains(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"");
}

test "lane05 mirror fallback contract preserves trusted fallback order" {
    try expectBefore(
        workflow,
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    );
    try expectBefore(
        workflow,
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail " ++ mirror_index_url ++ " -o \"$mirror_file\"; then",
    );
    try expectBefore(
        workflow,
        "elif curl -L --fail " ++ mirror_index_url ++ " -o \"$mirror_file\"; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    );
}

test "lane05 mirror fallback contract guards mirror loop shape" {
    try expectExactlyOnce(workflow, "curl -L --fail " ++ mirror_index_url ++ " -o \"$mirror_file\"");
    try expectExactlyOnce(workflow, "while IFS= read -r mirror_url; do");
    try expectContains(workflow, "[ -n \"$mirror_url\" ] || continue");
    try expectContains(
        workflow,
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME" ++ mirror_bootstrap_query ++ "\"",
    );
    try expectBefore(
        workflow,
        "[ -n \"$mirror_url\" ] || continue",
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME" ++ mirror_bootstrap_query ++ "\"",
    );
    try expectBefore(
        workflow,
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME" ++ mirror_bootstrap_query ++ "\"",
        "done < \"$mirror_file\"",
    );
}

test "lane05 mirror fallback contract clears stale download state" {
    try expectContains(workflow, "mirror_file=\".zig-toolchain/community-mirrors.txt\"");
    try expectContains(workflow, "rm -f \"$archive_path\" \"$mirror_file\"");
    try expectContains(workflow, "rm -rf \"$extract_root\"");
    try expectBefore(
        workflow,
        "rm -f \"$archive_path\" \"$mirror_file\"",
        "try_local_archive() {",
    );
    try expectBefore(
        workflow,
        "rm -rf \"$extract_root\"",
        "try_download() {",
    );
}

test "lane05 mirror fallback contract keeps shipped README reminder explicit" {
    try expectContains(
        third_party_readme,
        "canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL",
    );
    try expectContains(
        third_party_readme,
        "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle",
    );
    try expectContains(
        third_party_readme,
        "duplicate-suffix archives are rejected before staging",
    );
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectContains(workflow, direct_builds_url);
}
