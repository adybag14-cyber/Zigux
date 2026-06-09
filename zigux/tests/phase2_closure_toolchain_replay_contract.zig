const std = @import("std");
const testing = std.testing;

const Contract = struct {
    allocator: std.mem.Allocator,

    fn readFile(self: Contract, relative_path: []const u8) ![]u8 {
        return std.Io.Dir.cwd().readFileAlloc(
            testing.io,
            relative_path,
            self.allocator,
            .limited(1024 * 1024),
        );
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{needle});
            return error.MissingMarker;
        };
        cursor += found + needle.len;
    }
}

test "tests-root and scripts-root keep toolchain replay commands explicit" {
    const contract = Contract{ .allocator = testing.allocator };

    const tests_readme = try contract.readFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const scripts_readme = try contract.readFile("scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);

    const replay_markers = [_][]const u8{
        "scripts/zigux/check-zig-toolchain.py",
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "scripts/zigux/install-zig.py",
        "python3 scripts/zigux/install-zig.py --self-test",
        "make -C zigux phase2-toolchain",
    };

    for (replay_markers) |marker| {
        try expectContains(tests_readme, marker);
        try expectContains(scripts_readme, marker);
    }

    try expectContains(tests_readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(tests_readme, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz --archive-target x86_64-linux");
    try expectContains(scripts_readme, "canonical Zig release bootstrap path");
}

test "manifest keeps toolchain, installer, archive, and policy surfaces split" {
    const contract = Contract{ .allocator = testing.allocator };

    const manifest = try contract.readFile("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(manifest);

    const required_manifest_markers = [_][]const u8{
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/check-phase2-toolchain-pinning.py\"",
        "\"scripts/zigux/check-phase2-toolchain-pin-scope.py\"",
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"third_party/README.md\"",
        "\"third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\"",
        "\"scripts/zigux/zig-toolchain-policy.json\"",
        "\"make -C zigux phase2-toolchain\"",
    };

    for (required_manifest_markers) |marker| {
        try expectContains(manifest, marker);
    }

    try expectContains(manifest, "\"archive_support\"");
    try expectContains(manifest, "\"bootstrap_helpers\"");
    try expectContains(manifest, "\"policy\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
}

test "workflow replays toolchain verification before Phase 2 aggregate routes" {
    const contract = Contract{ .allocator = testing.allocator };

    const workflow = try contract.readFile(".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);

    try expectInOrder(workflow, &[_][]const u8{
        "name: Setup pinned Zig toolchain",
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
        "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
        "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "python3 scripts/zigux/install-zig.py --self-test",
        "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
        "python3 scripts/zigux/check-phase2-toolchain-pinning.py",
        "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    });
}

test "makefile keeps phase2-toolchain as the shared Phase 2 prerequisite" {
    const contract = Contract{ .allocator = testing.allocator };

    const makefile = try contract.readFile("zigux/Makefile");
    defer testing.allocator.free(makefile);

    try expectInOrder(makefile, &[_][]const u8{
        "phase2-toolchain:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    });
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py");
    try expectContains(makefile, "phase2-tools: phase2-toolchain");
    try expectContains(makefile, "phase2-kconfig: phase2-toolchain");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2-genksyms: phase2-toolchain");
    try expectContains(makefile, "phase2-fixdep: phase2-toolchain");
}
