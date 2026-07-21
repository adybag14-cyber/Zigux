const std = @import("std");

const manifest_text = @embedFile("fixtures/phase2_tool_manifest.json");

const toolchain_manifest_markers = [_][]const u8{
    "\"archive_support\"",
    "\"bootstrap_helpers\"",
    "\"policy\"",
    "\"make_wrappers\"",
    "\"scripts\zigux/check_zig_toolchain.zig\"",
    "\"scripts\zigux/check_lane05_local_first_archive_workflow.zig\"",
    "\"scripts\zigux/check_lane05_local_archive_readme.zig\"",
    "\"scripts\zigux/check_lane05_install_zig_archive_verification.zig\"",
    "\"scripts\zigux/check_lane05_stage_helper_contract.zig\"",
    "\"scripts\zigux/check_lane05_stage_helper_selftest.zig\"",
    "\"scripts/zigux/install_zig.zig\"",
    "\"scripts/zigux/stage_pinned_zig_archive.zig\"",
    "\"third_party/README.md\"",
    "\"scripts/zigux/zig-toolchain-policy.json\"",
    "\"make -C zigux phase2-toolchain\"",
};

const toolchain_make_commands = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_first_archive_workflow.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_first_archive_workflow.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_archive_readme.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_archive_readme.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_install_zig_archive_verification.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_install_zig_archive_verification.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install_zig.zig --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage_pinned_zig_archive.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_contract.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_contract.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_selftest.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_selftest.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-tools:",
};

const toolchain_workflow_runs = [_][]const u8{
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test",
    "run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts/zigux/check_phase2_toolchain_pinning.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase2_toolchain_pinning.zig",
    "run: zig run scripts/zigux/check_phase2_toolchain_pin_scope.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase2_toolchain_pin_scope.zig",
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
        "        run: zig run scripts/zigux/check_lane05_install_zig_archive_verification.zig\n",
        1,
    );
    try requireExactCount(
        workflow_text,
        "        run: zig run scripts/zigux/check_lane05_stage_helper_selftest.zig\n",
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
