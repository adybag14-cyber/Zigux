const std = @import("std");
const routes = @import("bootstrap_toolchain_route_contract.zig");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const install_zig_path = "scripts/zigux/install_zig.zig";
const check_zig_toolchain_path = "scripts/zigux/check_zig_toolchain.zig";
const toolchain_resolver_path = "scripts/zigux/toolchain_resolver.zig";

const pinned_channel = "0.17.0-dev.877+a3ae499dc";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-a3ae499dc297";

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

    try expectContains(installer, "pub const canonical_release_channel = \"" ++ pinned_channel ++ "\"");
    try expectContains(installer, "pub const default_canonical_release_repo = \"" ++ canonical_repo ++ "\"");
    try expectContains(installer, "pub const default_canonical_release_tag = \"" ++ canonical_tag ++ "\"");
    try expectContains(installer, "https://github.com/{s}/releases/download/{s}/zig-{s}-{s}{s}");
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
    try routes.requireRoute(workflow, routes.stage_python, routes.stage_zig);
    try routes.requireRoute(workflow, routes.archive_check_python, routes.archive_check_zig);
    try expectContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try routes.requireRoute(workflow, routes.zig_probe_python, routes.zig_probe_zig);

    try expectBefore(workflow, "try_local_archive() {", "try_download() {");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    const parts_index = std.mem.indexOf(u8, workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"") orelse return error.MissingPartsDir;
    const stage_index = routes.routeIndex(workflow, routes.stage_python, routes.stage_zig) orelse return error.MissingStageRoute;
    try std.testing.expect(parts_index < stage_index);
}

test "network fallback order stays canonical release, mirrors, then ziglang builds" {
    const workflow = try readRepoFile(workflow_path);
    defer std.testing.allocator.free(workflow);
    const checker = try readRepoFile(check_zig_toolchain_path);
    defer std.testing.allocator.free(checker);
    const resolver = try readRepoFile(toolchain_resolver_path);
    defer std.testing.allocator.free(resolver);

    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectContains(workflow, "\"$zig_path\" version");

    try expectContains(checker, "resolver.validatePolicyArchive");
    try expectContains(resolver, "policy.archiveNameMatchesPolicy");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256");
    try expectContains(checker, "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256");
}
