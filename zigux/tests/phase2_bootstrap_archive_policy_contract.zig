const std = @import("std");

const allocator = std.testing.allocator;

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const pinned_filename = "zig-x86_64-linux-" ++ pinned_channel ++ ".tar.xz";
const pinned_archive_path = "third_party/" ++ pinned_filename;
const pinned_parts_path = pinned_archive_path ++ ".parts";
const canonical_release_repo = "adybag14-cyber/zig";
const canonical_release_tag = "upstream-748e7c5e39fc";
const canonical_release_url = "https://github.com/" ++ canonical_release_repo ++ "/releases/download/" ++ canonical_release_tag ++ "/" ++ pinned_filename;

fn readRootFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
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

test "toolchain policy pins the exact current bootstrap archive contract" {
    const policy = try readRootFile("scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
    try expectBefore(policy, "\"phase2-toolchain\"", "\"phase2-validate\"");
}

test "third party archive note preserves exact local archive and shard handoff" {
    const readme = try readRootFile("third_party/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "- target: `" ++ pinned_target ++ "`");
    try expectContains(readme, "- channel: `" ++ pinned_channel ++ "`");
    try expectContains(readme, "- file: `" ++ pinned_archive_path ++ "`");
    try expectContains(readme, "- sha256: `" ++ pinned_sha256 ++ "`");
    try expectContains(readme, "- size: `59410844` bytes");
    try expectContains(readme, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++ pinned_archive_path ++ " --archive-target " ++ pinned_target);
    try expectContains(readme, pinned_parts_path);
    try expectContains(readme, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(readme, "canonical `" ++ canonical_release_repo ++ "` release");
    try expectBefore(readme, pinned_archive_path, canonical_release_repo);
}

test "bootstrap workflow keeps local archive before canonical release and network fallbacks" {
    const workflow = try readRootFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectContains(workflow, "canonical_repo = \"" ++ canonical_release_repo ++ "\"");
    try expectContains(workflow, "canonical_tag = \"" ++ canonical_release_tag ++ "\"");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
}

test "workflow and installers expose policy, archive-only, and canonical self-test checks" {
    const workflow = try readRootFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const installer = try readRootFile("scripts/zigux/install-zig.py");
    defer allocator.free(installer);
    const checker = try readRootFile("scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow, "python3 scripts/zigux/install-zig.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectBefore(workflow, "--policy-only", "--archive-only --allow-missing");

    try expectContains(installer, "CANONICAL_RELEASE_CHANNEL = '" ++ pinned_channel ++ "'");
    try expectContains(installer, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_release_repo ++ "')");
    try expectContains(installer, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_release_tag ++ "')");
    try expectContains(installer, canonical_release_url);
    try expectContains(installer, "ZIG_INSTALL_SELF_TEST=pass");

    try expectContains(checker, "FALLBACK_MIN_VERSION = \"0.16.0\"");
    try expectContains(checker, "add_search_root(root / \"third_party\")");
    try expectContains(checker, "add_search_root(root / \"agent_files\")");
    try expectContains(checker, "--archive-only");
    try expectContains(checker, "--allow-missing");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
}
