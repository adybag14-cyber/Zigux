const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-toolchain-pinning.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const bootstrap_notes_path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const scripts_readme_path = "scripts/zigux/README.md";
const tool_manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_offset = std.mem.indexOf(u8, haystack[before_index..], after) orelse return error.MissingAfterMarker;
    try std.testing.expect(after_offset > 0);
}

fn countExactLines(haystack: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectExactWorkflowLine(workflow: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(workflow, marker));
}

test "toolchain pinning checker owns the live phase two surface roster" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"\"\"Guard the current directly readable Phase 2 toolchain pinning packet.\"\"\"");
    try expectContains(checker, "ARCHIVE_TARGET = \"x86_64-linux\"");
    try expectContains(checker, "ARCHIVE_CHANNEL = \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(checker, "ARCHIVE_SIZE = 59_410_844");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 52");
    try expectContains(checker, "\"scripts/zigux/check-zig-toolchain.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-toolchain-pinning.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase2-toolchain-pin-scope.py\"");
    try expectContains(checker, "\"scripts/zigux/install-zig.py\"");
    try expectContains(checker, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(checker, "\"scripts/zigux/kconfig/conf_bridge.zig\"");
    try expectContains(checker, "\"scripts/zigux/genksyms.zig\"");
    try expectContains(checker, "\"scripts/zigux/fixdep.zig\"");
    try expectContains(checker, "\"zigux/tests/fixtures/phase2_tool_manifest.json\"");
}

test "policy and checker keep the exact pinned archive contract aligned" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");

    try expectInOrder(checker, "POLICY_EXPECTED = {", "\"phase\": \"Phase 2\"");
    try expectInOrder(checker, "POLICY_EXPECTED = {", "\"channel_minimum_lockstep\": True");
    try expectInOrder(checker, "\"required_make_routes\": [", "\"phase2-toolchain\"");
    try expectInOrder(checker, "\"required_make_routes\": [", "\"phase2-validate\"");
}

test "workflow and reminder surfaces expose both pinning routes exactly once" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const notes = try readRepoFile(allocator, bootstrap_notes_path);
    defer allocator.free(notes);
    const scripts_readme = try readRepoFile(allocator, scripts_readme_path);
    defer allocator.free(scripts_readme);

    try expectExactWorkflowLine(workflow, "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test");
    try expectExactWorkflowLine(workflow, "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py");
    try expectExactWorkflowLine(workflow, "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test");
    try expectExactWorkflowLine(workflow, "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py");
    try expectExactWorkflowLine(workflow, "run: make -C zigux phase2-toolchain");

    try expectContains(notes, "`scripts/zigux/check-phase2-toolchain-pinning.py`");
    try expectContains(notes, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try expectContains(notes, "pinned-channel probe");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-toolchain-pinning.py`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
}

test "tool manifest keeps the pinning checker in the phase two tool packet" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, tool_manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-toolchain-pinning.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-toolchain-pin-scope.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-zig-toolchain.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-toolchain\"");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
}
