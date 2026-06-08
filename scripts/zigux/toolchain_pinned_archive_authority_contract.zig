const std = @import("std");

const pinned_target = "x86_64-linux";
const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_size = "59410844";
const pinned_filename = "zig-" ++ pinned_target ++ "-" ++ pinned_channel ++ ".tar.xz";
const pinned_archive_path = "third_party/" ++ pinned_filename;
const pinned_parts_path = pinned_archive_path ++ ".parts";
const canonical_release_repo = "adybag14-cyber/zig";
const canonical_release_tag = "upstream-748e7c5e39fc";

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "policy pins the current trusted Zig archive authority" {
    const policy = try readFile("scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
    try expectNotContains(policy, "0.17.0-dev.87+9b177a7d2");
}

test "third party README mirrors the live archive contract and duplicate-copy boundary" {
    const readme = try readFile("third_party/README.md");
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "- target: `" ++ pinned_target ++ "`");
    try expectContains(readme, "- channel: `" ++ pinned_channel ++ "`");
    try expectContains(readme, "- file: `" ++ pinned_archive_path ++ "`");
    try expectContains(readme, "- sha256: `" ++ pinned_sha256 ++ "`");
    try expectContains(readme, "- size: `" ++ pinned_size ++ "` bytes");
    try expectContains(readme, "--archive " ++ pinned_archive_path ++ " --archive-target " ++ pinned_target);
    try expectContains(readme, "`" ++ pinned_parts_path ++ "`");
    try expectContains(readme, "canonical `" ++ canonical_release_repo ++ "` release");
    try expectContains(readme, "duplicate-suffix archives are rejected before staging");
    try expectContains(readme, "update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json`");
}

test "workflow keeps local archive and staged parts before network fallback" {
    const workflow = try readFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "canonical_repo = \"" ++ canonical_release_repo ++ "\"");
    try expectContains(workflow, "canonical_tag = \"" ++ canonical_release_tag ++ "\"");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectOrder(workflow, "https://ziglang.org/download/community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
}

test "checker exposes archive diagnostics for the same pinned payload" {
    const checker = try readFile("scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "ARCHIVE_DUPLICATE_SUFFIX_RE");
    try expectContains(checker, "policy_archive_filename");
    try expectContains(checker, "archive_name_has_duplicate_suffix");
    try expectContains(checker, "multiple repo-local pinned archive candidates matched");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS");
    try expectContains(checker, "root / \"third_party\"");
    try expectContains(checker, "root / \"agent_files\"");
    try expectContains(checker, pinned_channel);
    try expectContains(checker, pinned_filename);
    try expectNotContains(checker, "0.17.0-dev.87+9b177a7d2");
}
