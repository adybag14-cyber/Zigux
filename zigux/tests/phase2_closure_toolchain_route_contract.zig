const std = @import("std");

const manifest_text = @embedFile("fixtures/phase2_tool_manifest.json");

const toolchain_manifest_markers = [_][]const u8{
    "\"archive_support\"",
    "\"bootstrap_helpers\"",
    "\"policy\"",
    "\"make_wrappers\"",
    "\"scripts/zigux/check-zig-toolchain.py\"",
    "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"",
    "\"scripts/zigux/check-lane05-local-archive-readme.py\"",
    "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
    "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
    "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    "\"scripts/zigux/install-zig.py\"",
    "\"scripts/zigux/stage-pinned-zig-archive.py\"",
    "\"third_party/README.md\"",
    "\"scripts/zigux/zig-toolchain-policy.json\"",
    "\"make -C zigux phase2-toolchain\"",
};

const toolchain_make_commands = [_][]const u8{
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
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
    "phase2-tools:",
};

const toolchain_workflow_runs = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, marker);
        try std.testing.expect(found != null);
        cursor = found.? + marker.len;
    }
}

fn requireExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "closure manifest keeps toolchain bootstrap surfaces explicit" {
    for (toolchain_manifest_markers) |marker| {
        try requireContains(manifest_text, marker);
    }
}

test "phase2-toolchain make wrapper preserves local archive and stage-helper order" {
    const makefile_text = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "zigux/Makefile",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(makefile_text);

    try requireOrder(makefile_text, &toolchain_make_commands);

    try requireExactCount(makefile_text, "phase2-toolchain:", 1);
    try requireContains(makefile_text, "phase2-kconfig: phase2-toolchain");
    try requireContains(makefile_text, "phase2-genksyms: phase2-toolchain");
    try requireContains(makefile_text, "phase2-fixdep: phase2-toolchain");
}

test "bootstrap workflow preserves the current toolchain route subpacket" {
    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(workflow_text);

    try requireOrder(workflow_text, &toolchain_workflow_runs);

    try requireExactCount(
        workflow_text,
        "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\n",
        1,
    );
    try requireExactCount(
        workflow_text,
        "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\n",
        1,
    );
    try requireOrder(workflow_text, &[_][]const u8{
        "run: make -C zigux phase2-toolchain",
        "run: make -C zigux phase2-tools",
        "run: make -C zigux phase2-kconfig",
        "run: make -C zigux phase2-fixdep",
        "run: make -C zigux phase2-cross",
    });
}
