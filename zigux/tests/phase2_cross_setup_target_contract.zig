const std = @import("std");

const allocator = std.testing.allocator;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(!contains(haystack, needle));
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

test "workflow setup derives the pinned archive target from policy scope" {
    const workflow = try readRepoFile(workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text");
    try expectContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(workflow, "if len(targets) != 1:");
    try expectContains(workflow, "expected exactly one pinned archive target");
    try expectContains(workflow, "target = targets[0]");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_TARGET='{target}'\")");
    try expectContains(workflow, "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")");
    try expectOrdered(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]", "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectOrdered(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"", "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"");
}

test "workflow verification keeps archive-only checks scoped to the selected target" {
    const workflow = try readRepoFile(workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "expected exactly one pinned archive target"));
}

test "policy keeps one archive-backed target for the Phase 2 cross matrix" {
    const policy = try readRepoFile(policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"archive_sha256\": {");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\"");
    try expectOrdered(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
}

test "fixture keeps aarch64 route-only while setup owns x86 archive materialization" {
    const fixture = try readRepoFile(fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
}
