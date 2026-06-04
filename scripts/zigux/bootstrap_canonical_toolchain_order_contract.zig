const std = @import("std");

const canonical_channel = "0.17.0-dev.758+748e7c5e3";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";
const canonical_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const max_file_bytes = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_bytes),
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

test "bootstrap setup derives canonical release coordinates from the live policy channel" {
    const allocator = std.testing.allocator;
    const workflow_source = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_source);
    const policy_source = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy_source);

    try expectContains(policy_source, "\"channel\": \"" ++ canonical_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ canonical_channel ++ "\"");
    try expectContains(policy_source, "\"x86_64-linux\": \"" ++ canonical_digest ++ "\"");

    try expectContains(workflow_source, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try expectContains(workflow_source, "canonical_tag = \"" ++ canonical_tag ++ "\"");
    try expectContains(workflow_source, "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"");
    try expectContains(workflow_source, "print(f\"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'\")");
    try expectContains(workflow_source, "filename = f\"zig-{target}-{channel}.tar.xz\"");
}

test "bootstrap setup keeps trusted local and canonical sources ahead of network fallbacks" {
    const allocator = std.testing.allocator;
    const workflow_source = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow_source);

    try expectContains(workflow_source, "try_local_archive");
    try expectContains(workflow_source, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectContains(workflow_source, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow_source, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectContains(workflow_source, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");

    try expectBefore(workflow_source, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow_source, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow_source, "https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "installer and workflow agree on the canonical release before generic dev builds" {
    const allocator = std.testing.allocator;
    const install_zig_source = try readRepoFile(allocator, "scripts/zigux/install-zig.py");
    defer allocator.free(install_zig_source);

    try expectContains(install_zig_source, "CANONICAL_RELEASE_CHANNEL = '" ++ canonical_channel ++ "'");
    try expectContains(install_zig_source, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try expectContains(install_zig_source, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");
    try expectBefore(
        install_zig_source,
        "if channel == CANONICAL_RELEASE_CHANNEL:",
        "if '-dev.' in channel:",
    );
    try expectBefore(
        install_zig_source,
        "if channel == CANONICAL_RELEASE_CHANNEL:\n        return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
        "entry = index.get(channel)",
    );
}
