const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countContains(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "phase2 cross workflow derives pinned Zig archive identity from policy" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try expectContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(workflow, "if len(targets) != 1:");
    try expectContains(workflow, "channel = policy[\"channel\"]");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_TARGET='{target}'\")");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")");
    try expectContains(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectBefore(workflow, "Setup pinned Zig toolchain", "Self-test current Phase 2 cross checker");
}

test "phase2 cross workflow keeps verified archive source fallback order" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "try_local_archive() {");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
}

test "phase2 cross workflow runs direct checker packet after pinned setup" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    const setup = "Setup pinned Zig toolchain";
    const direct_self_test = "Self-test current Phase 2 cross checker";
    const direct_check = "Check current Phase 2 direct cross-route packet";
    const alignment_self_test = "Self-test current Phase 2 cross selftest alignment checker";
    const alignment_check = "Check current Phase 2 cross alignment packet";
    const make_route = "Run current Phase 2 cross make route";

    try expectBefore(workflow, setup, direct_self_test);
    try expectBefore(workflow, direct_self_test, direct_check);
    try expectBefore(workflow, direct_check, alignment_self_test);
    try expectBefore(workflow, alignment_self_test, alignment_check);
    try expectBefore(workflow, alignment_check, make_route);
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross.py");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(workflow, "run: make -C zigux phase2-cross");
}

test "phase2 cross policy and fixture keep current two-target boundary" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
    try std.testing.expectEqual(@as(usize, 2), countContains(fixture, "\"target\": "));
}
