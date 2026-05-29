const std = @import("std");

const repo_file_limit = 1024 * 1024;

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(repo_file_limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countExactWorkflowLine(workflow: []const u8, line: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, workflow, '\n');
    while (lines.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, " \t"), line)) {
            count += 1;
        }
    }
    return count;
}

fn expectOneWorkflowLine(workflow: []const u8, line: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactWorkflowLine(workflow, line));
}

test "lane05 bootstrap validator keeps the local archive checker roster required" {
    const validator = try readRepoFile("scripts/zigux/validate-bootstrap.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(validator, "scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(validator, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(validator, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(validator, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(validator, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(validator, "scripts/zigux/zig-toolchain-policy.json");
}

test "lane05 bootstrap validator keeps each workflow line guarded once" {
    const validator = try readRepoFile("scripts/zigux/validate-bootstrap.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(validator, "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py");
}

test "lane05 bootstrap workflow keeps local parts reconstruction ahead of fallback downloads" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");

    const local_route = std.mem.indexOf(u8, workflow, "if try_local_archive; then") orelse return error.MissingLocalRoute;
    const mirror_route = std.mem.indexOf(u8, workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt") orelse return error.MissingMirrorRoute;
    const direct_route = std.mem.indexOf(u8, workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then") orelse return error.MissingDirectRoute;
    try std.testing.expect(local_route < mirror_route);
    try std.testing.expect(mirror_route < direct_route);
}

test "lane05 bootstrap workflow keeps checker invocations unique" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test");
    try expectOneWorkflowLine(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py");
}
