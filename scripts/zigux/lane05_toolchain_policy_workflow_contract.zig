const std = @import("std");

const current_channel = "0.17.0-dev.758+748e7c5e3";
const current_target = "x86_64-linux";
const current_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const current_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const canonical_repo = "adybag14-cyber/zig";
const canonical_tag = "upstream-748e7c5e39fc";

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

    try requireOrdered(workflow, &.{
        "try_local_archive() {",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "--parts-dir \"$repo_archive_parts_dir\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "try_download() {",
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "community-mirrors.txt",
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"",
        "try_download \"$ZIGUX_ZIG_URL\"",
        "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    });
}

test "bootstrap workflow keeps setup and early policy gates fail-closed" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "name: Checkout workspace snapshot",
        "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}",
        "name: Setup Python",
        "name: Setup pinned Zig toolchain",
        "name: Compile current scripts",
        "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
        "if [ \"${#scripts[@]}\" -eq 0 ]; then",
        "python3 -m py_compile \"${scripts[@]}\"",
        "name: Self-test current Zig toolchain checker",
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "name: Check current Zig toolchain policy packet",
        "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "name: Check current pinned Zig archive packet",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    });

    try requireExactlyOnce(workflow, "name: Setup pinned Zig toolchain");
    try requireAbsent(workflow, "uses: actions/checkout@");
    try requireAbsent(workflow, "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2");
}

test "installer helper canonical release constants match live policy channel" {
    const installer = try readRepoFile(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer);

    try requireContains(installer, "CANONICAL_RELEASE_CHANNEL = '" ++ current_channel ++ "'");
    try requireContains(installer, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', '" ++ canonical_repo ++ "')");
    try requireContains(installer, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', '" ++ canonical_tag ++ "')");
    try requireContains(installer, "def load_policy_archive_sha256");
    try requireContains(installer, "def verify_archive_sha256");
    try requireContains(installer, "DOWNLOAD_RETRIES = 4");
    try requireContains(installer, "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");

    try requireAbsent(installer, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.87+9b177a7d2'");
}
