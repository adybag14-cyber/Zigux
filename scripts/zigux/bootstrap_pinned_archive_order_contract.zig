const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const install_zig_path = "scripts/zigux/install-zig.py";
const check_zig_toolchain_path = "scripts/zigux/check-zig-toolchain.py";

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "pinned policy and installer keep the canonical archive identity aligned" {
    const policy = try readRepoFile(policy_path);
    defer std.testing.allocator.free(policy);
    const installer = try readRepoFile(install_zig_path);
    defer std.testing.allocator.free(installer);

    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"" ++ pinned_target ++ "\"");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");

    try expectContains(installer, "CANONICAL_RELEASE_CHANNEL = '" ++ pinned_channel ++ "'");
    try expectContains(installer, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try expectContains(installer, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");
    try expectContains(installer, "https://github.com/{CANONICAL_RELEASE_REPO}/releases/download/");
}

test "workflow derives a single pinned archive name from policy before setup" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(workflow, "if len(targets) != 1:");
    try expectContains(workflow, "target = targets[0]");
    try expectContains(workflow, "channel = policy[\"channel\"]");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try expectContains(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"");
    try expectContains(workflow, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")");
}

test "local archive and staged parts are tried before network fallbacks" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");

    try expectBefore(workflow, "try_local_archive() {", "try_download() {");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"", "python3 scripts/zigux/stage-pinned-zig-archive.py");
}

test "network fallback order stays canonical release, mirrors, then ziglang builds" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);
    const checker = try readRepoFile(check_zig_toolchain_path);
    defer std.testing.allocator.free(checker);

    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectContains(workflow, "\"$zig_path\" version");

    try expectContains(checker, "archive_name_matches_policy");
    try expectContains(checker, "validate_policy_archive");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256");
}
