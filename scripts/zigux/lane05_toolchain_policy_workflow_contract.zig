const std = @import("std");
const routes = @import("bootstrap_toolchain_route_contract.zig");

const current_channel = "0.17.0-dev.877+a3ae499dc";
const current_target = "x86_64-linux";
const current_digest = "c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8";
const current_filename = "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-a3ae499dc297";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle);
        try std.testing.expect(found != null);
        cursor += found.? + needle.len;
    }
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try std.testing.expect(first != null);
    const after_first = first.? + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
}

test "toolchain policy pins current trusted bootstrap archive identity" {
    const policy = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    try requireContains(policy, "\"channel\": \"" ++ current_channel ++ "\"");
    try requireContains(policy, "\"minimum_version\": \"" ++ current_channel ++ "\"");
    try requireContains(policy, "\"" ++ current_target ++ "\": \"" ++ current_digest ++ "\"");
    try requireContains(policy, "\"channel_minimum_lockstep\": true");
    try requireContains(policy, "\"archive_target_scope\"");
    try requireContains(policy, "\"" ++ current_target ++ "\"");

    try requireAbsent(policy, "0.17.0-dev.87+9b177a7d2");
    try requireAbsent(policy, "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77");
}

test "bootstrap workflow derives archive filename and probes local trusted bytes first" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "name: Setup pinned Zig toolchain");
    try requireContains(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text");
    try requireContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try requireContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(workflow, "canonical_repo = \"" ++ canonical_repo ++ "\"");
    try requireContains(workflow, "canonical_tag = \"" ++ canonical_tag ++ "\"");
    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");

    const local_index = std.mem.indexOf(u8, workflow, "try_local_archive() {") orelse return error.MissingLocalArchive;
    const stage_index = routes.routeIndex(workflow, routes.stage_python, routes.stage_zig) orelse return error.MissingStageRoute;
    const parts_index = std.mem.indexOf(u8, workflow, "--parts-dir \"$repo_archive_parts_dir\"") orelse return error.MissingPartsArg;
    const archive_index = routes.routeIndex(workflow, routes.archive_check_python, routes.archive_check_zig) orelse return error.MissingArchiveRoute;
    const download_index = std.mem.indexOf(u8, workflow, "try_download() {") orelse return error.MissingDownloadHelper;
    const attempt_index = std.mem.indexOf(u8, workflow, "if try_local_archive; then") orelse return error.MissingLocalAttempt;
    const canonical_index = std.mem.indexOf(u8, workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then") orelse return error.MissingCanonicalFallback;
    const mirrors_index = std.mem.indexOf(u8, workflow[canonical_index..], "elif curl --fail") orelse return error.MissingMirrorsFallback;
    const mirrors_abs_index = canonical_index + mirrors_index;
    const mirror_try_index = std.mem.indexOf(u8, workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"") orelse return error.MissingMirrorAttempt;
    const direct_index = std.mem.indexOf(u8, workflow, "try_download \"$ZIGUX_ZIG_URL\"") orelse return error.MissingDirectFallback;
    const failure_index = std.mem.indexOf(u8, workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org") orelse return error.MissingFailureMessage;
    try std.testing.expect(local_index < stage_index);
    try std.testing.expect(stage_index < parts_index);
    try std.testing.expect(parts_index < archive_index);
    try std.testing.expect(archive_index < download_index);
    try std.testing.expect(download_index < attempt_index);
    try std.testing.expect(attempt_index < canonical_index);
    try std.testing.expect(canonical_index < mirrors_abs_index);
    try std.testing.expect(mirrors_abs_index < mirror_try_index);
    try std.testing.expect(mirror_try_index < direct_index);
    try std.testing.expect(direct_index < failure_index);
}

test "bootstrap workflow keeps setup and early policy gates fail-closed" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "name: Checkout workspace snapshot",
        "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}",
        "name: Setup Python",
        "name: Setup pinned Zig toolchain",
        "name: Validate current Zig bootstrap helpers",
        "zig test scripts/zigux/toolchain_policy.zig",
        "zig test scripts/zigux/install_zig.zig",
        "name: Self-test current Zig toolchain checker",
        "zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
        "name: Check current Zig toolchain policy packet",
        "zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
        "name: Check current pinned Zig archive packet",
        "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    });

    try requireExactlyOnce(workflow, "name: Setup pinned Zig toolchain");
    try requireAbsent(workflow, "uses: actions/checkout@");
    try requireAbsent(workflow, "zig run scripts/zigux/install_zig.zig -- --channel 0.17.0-dev.87+9b177a7d2");
}

test "installer helper canonical release constants match live policy channel" {
    const installer = try readRepoFile(std.testing.allocator, "scripts/zigux/install_zig.zig");
    defer std.testing.allocator.free(installer);

    try requireContains(installer, "pub const canonical_release_channel = \"" ++ current_channel ++ "\"");
    try requireContains(installer, "pub const default_canonical_release_repo = \"" ++ canonical_repo ++ "\"");
    try requireContains(installer, "pub const default_canonical_release_tag = \"" ++ canonical_tag ++ "\"");
    try requireContains(installer, "pub fn loadPolicyArchiveSha256");
    try requireContains(installer, "pub fn verifyArchiveSha256");
    try requireContains(installer, "pub const download_retries: u32 = 4");
    try requireContains(installer, "pub const retryable_http_status_codes = [_]u16{ 408, 429, 500, 502, 503, 504 }");

    try requireAbsent(installer, "0.17.0-dev.87+9b177a7d2");
}
