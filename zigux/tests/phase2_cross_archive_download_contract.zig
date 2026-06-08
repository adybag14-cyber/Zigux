const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, std.Io.Limit.limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "workflow derives the pinned x86 archive identity from policy" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");

    try expectContains(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try expectContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(workflow, "ZIGUX_ZIG_CANONICAL_URL");
}

test "workflow keeps local archive before canonical, mirror, and ziglang fallbacks" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "try_local_archive() {");
    try expectContains(workflow, "try_download() {");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "?source=github-zigux-bootstrap");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");

    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "workflow verifies every archive source before extraction and path publication" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"", "return 0");
    try expectBefore(workflow, "download_success=0", "if [ \"$download_success\" -ne 1 ]; then");
    try expectBefore(workflow, "if [ \"$download_success\" -ne 1 ]; then", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectBefore(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"", "\"$zig_path\" version");
}

test "workflow keeps the Phase 2 cross route tied to the archive-backed target packet" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(workflow, "ZIGUX_ZIG_TARGET='{target}'");
    try expectContains(workflow, "--archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"");
}
