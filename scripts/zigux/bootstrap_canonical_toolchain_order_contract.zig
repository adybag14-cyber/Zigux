const std = @import("std");

const canonical_channel = "0.17.0-dev.877+a3ae499dc";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-a3ae499dc297";
const canonical_digest = "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8";
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
    const install_zig_source = try readRepoFile(allocator, "scripts/zigux/install_zig.zig");
    defer allocator.free(install_zig_source);

    try expectContains(install_zig_source, "pub const canonical_release_channel = \"" ++ canonical_channel ++ "\"");
    try expectContains(install_zig_source, "pub const default_canonical_release_repo = \"" ++ canonical_repo ++ "\"");
    try expectContains(install_zig_source, "pub const default_canonical_release_tag = \"" ++ canonical_tag ++ "\"");
    try expectContains(install_zig_source, "ZIGUX_ZIG_RELEASE_REPO");
    try expectContains(install_zig_source, "ZIGUX_ZIG_RELEASE_TAG");
    try expectBefore(
        install_zig_source,
        "if (std.mem.eql(u8, channel, canonical_release_channel))",
        "if (std.mem.indexOf(u8, channel, \"-dev.\"))",
    );
    try expectBefore(
        install_zig_source,
        "if (std.mem.eql(u8, channel, canonical_release_channel)) {",
        "var entry = index.get(channel);",
    );
}
