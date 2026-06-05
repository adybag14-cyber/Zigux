const std = @import("std");
const testing = std.testing;

const RepoFile = struct {
    path: []const u8,
};

const manifest_file = RepoFile{
    .path = "zigux/tests/fixtures/phase2_tool_manifest.json",
};
const makefile_file = RepoFile{
    .path = "zigux/Makefile",
};
const workflow_file = RepoFile{
    .path = ".github/workflows/zigux-bootstrap.yml",
};

fn readRepoFile(allocator: std.mem.Allocator, file: RepoFile) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, file.path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle) orelse {
            try testing.expect(false);
            return;
        };
        cursor += relative + needle.len;
    }
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    try testing.expectEqual(expected, count);
}

test "phase2 manifest keeps bootstrap helper roster explicit" {
    const allocator = testing.allocator;
    const manifest = try readRepoFile(allocator, manifest_file);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"bootstrap_helpers\"");
    try expectOrdered(manifest, &.{
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
    });
    try expectCount(manifest, "\"scripts/zigux/install-zig.py\"", 1);
    try expectCount(manifest, "\"scripts/zigux/stage-pinned-zig-archive.py\"", 1);

    try expectOrdered(manifest, &.{
        "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    });
    try expectContains(manifest, "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\"");
    try expectContains(manifest, "\"scripts/zigux/zig-toolchain-policy.json\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
}

test "phase2 Makefile runs staged archive helpers before pinning guards" {
    const allocator = testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_file);
    defer allocator.free(makefile);

    try expectContains(makefile, "phase2-toolchain:");
    try expectOrdered(makefile, &.{
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    });
}

test "bootstrap workflow preserves local archive fallback and stage-helper checks" {
    const allocator = testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_file);
    defer allocator.free(workflow);

    try expectOrdered(workflow, &.{
        "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
        "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    });

    try expectOrdered(workflow, &.{
        "Self-test current Lane 05 install-zig archive verification checker",
        "Check current Lane 05 install-zig archive verification packet",
        "Self-test current staged pinned Zig archive helper",
        "Self-test current Zig installer helper",
        "Self-test current Lane 05 stage helper contract checker",
        "Check current Lane 05 stage helper contract packet",
        "Self-test current Lane 05 stage helper selftest checker",
        "Check current Lane 05 stage helper selftest packet",
    });
}

test "bootstrap helper closure contract stays out of helper implementations" {
    const allocator = testing.allocator;
    const manifest = try readRepoFile(allocator, manifest_file);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"scope\": \"current directly readable scripts-root toolchain");
    try expectAbsent(manifest, "\"scripts/basic/fixdep.c\"");
    try expectAbsent(manifest, "\"scripts/kconfig/conf.c\"");
    try expectAbsent(manifest, "\"scripts/kconfig/confdata.c\"");
}
