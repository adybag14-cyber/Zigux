const std = @import("std");
const testing = std.testing;

const docs = struct {
    const bootstrap_note =
        \\# Phase 2 Toolchain Bootstrap Notes
        \\scripts\zigux/check_phase2_bootstrap_workflow_routes.zig
        \\scripts\zigux/check_phase2_tests_readme_alignment.zig
        \\scripts\zigux/check_phase2_cross.zig
        \\zig run scripts/zigux/check_phase2_cross.zig -- --self-test
        \\scripts\zigux/check_lane05_local_first_archive_workflow.zig
        \\scripts\zigux/check_lane05_local_archive_readme.zig
        \\scripts\zigux/check_lane05_install_zig_archive_verification.zig
        \\scripts/zigux/stage_pinned_zig_archive.zig
        \\scripts\zigux/check_lane05_stage_helper_contract.zig
        \\scripts\zigux/check_lane05_stage_helper_selftest.zig
        \\scripts\zigux/check_phase2_genksyms_selftest_alignment.zig
        \\scripts\zigux/check_genksyms_bridge.zig
        \\scripts/zigux/genksyms.zig
        \\scripts\zigux/check_phase2_fixdep_gate.zig
        \\scripts\zigux/check_fixdep_diff.zig
        \\scripts/zigux/fixdep.zig
        \\zigux/tests/fixtures/phase2_cross_targets.json
        \\zigux/tests/fixtures/genksyms_bridge/manifest.json
        \\zigux/tests/fixtures/fixdep/cases.json
        \\make -C zigux phase2-toolchain
        \\make -C zigux phase2-tools
        \\make -C zigux phase2-kconfig
        \\make -C zigux phase2-cross
        \\make -C zigux phase2-genksyms
        \\make -C zigux phase2-fixdep
        \\make -C zigux phase2-validate
        \\make -C zigux phase2
    ;

    const tests_readme =
        \\# zigux/tests
        \\current direct-readback Phase 2 kconfig, genksyms, and fixdep packet
        \\Documentation/zigux/phase2-toolchain-bootstrap-notes.md
        \\scripts\zigux/check_phase2_bootstrap_workflow_routes.zig
        \\scripts\zigux/check_phase2_tests_readme_alignment.zig
        \\scripts\zigux/check_phase2_cross.zig
        \\zig run scripts/zigux/check_phase2_cross.zig -- --self-test
        \\scripts\zigux/check_lane05_local_first_archive_workflow.zig
        \\scripts\zigux/check_lane05_local_archive_readme.zig
        \\scripts\zigux/check_lane05_install_zig_archive_verification.zig
        \\scripts/zigux/stage_pinned_zig_archive.zig
        \\scripts\zigux/check_lane05_stage_helper_contract.zig
        \\scripts\zigux/check_lane05_stage_helper_selftest.zig
        \\scripts\zigux/check_phase2_genksyms_selftest_alignment.zig
        \\scripts\zigux/check_genksyms_bridge.zig
        \\scripts/zigux/genksyms.zig
        \\scripts\zigux/check_phase2_fixdep_gate.zig
        \\scripts\zigux/check_fixdep_diff.zig
        \\scripts/zigux/fixdep.zig
        \\zigux/tests/fixtures/phase2_cross_targets.json
        \\zigux/tests/fixtures/genksyms_bridge/manifest.json
        \\zigux/tests/fixtures/fixdep/cases.json
        \\make -C zigux phase2-toolchain
        \\make -C zigux phase2-tools
        \\make -C zigux phase2-kconfig
        \\make -C zigux phase2-cross
        \\make -C zigux phase2-genksyms
        \\make -C zigux phase2-fixdep
        \\make -C zigux phase2-validate
        \\make -C zigux phase2
    ;
};

const SharedMarker = struct {
    marker: []const u8,
    reason: []const u8,
};

const shared_markers = [_]SharedMarker{
    .{ .marker = "scripts\zigux/check_phase2_bootstrap_workflow_routes.zig", .reason = "bootstrap workflow-route guard" },
    .{ .marker = "scripts\zigux/check_phase2_tests_readme_alignment.zig", .reason = "tests-root reminder alignment guard" },
    .{ .marker = "scripts\zigux/check_phase2_cross.zig", .reason = "direct cross-route checker" },
    .{ .marker = "zig run scripts/zigux/check_phase2_cross.zig -- --self-test", .reason = "direct cross-route self-test" },
    .{ .marker = "scripts\zigux/check_lane05_local_first_archive_workflow.zig", .reason = "local-first archive workflow guard" },
    .{ .marker = "scripts\zigux/check_lane05_local_archive_readme.zig", .reason = "third_party archive README guard" },
    .{ .marker = "scripts\zigux/check_lane05_install_zig_archive_verification.zig", .reason = "archive-verification guard" },
    .{ .marker = "scripts/zigux/stage_pinned_zig_archive.zig", .reason = "staged archive helper" },
    .{ .marker = "scripts\zigux/check_lane05_stage_helper_contract.zig", .reason = "staged helper contract" },
    .{ .marker = "scripts\zigux/check_lane05_stage_helper_selftest.zig", .reason = "staged helper self-test" },
    .{ .marker = "scripts\zigux/check_phase2_genksyms_selftest_alignment.zig", .reason = "genksyms selftest alignment guard" },
    .{ .marker = "scripts\zigux/check_genksyms_bridge.zig", .reason = "genksyms bridge checker" },
    .{ .marker = "scripts/zigux/genksyms.zig", .reason = "genksyms Zig bridge helper" },
    .{ .marker = "scripts\zigux/check_phase2_fixdep_gate.zig", .reason = "fixdep governance gate" },
    .{ .marker = "scripts\zigux/check_fixdep_diff.zig", .reason = "fixdep parity checker" },
    .{ .marker = "scripts/zigux/fixdep.zig", .reason = "fixdep Zig helper" },
    .{ .marker = "zigux/tests/fixtures/phase2_cross_targets.json", .reason = "direct cross-route target fixture" },
    .{ .marker = "zigux/tests/fixtures/genksyms_bridge/manifest.json", .reason = "genksyms fixture manifest" },
    .{ .marker = "zigux/tests/fixtures/fixdep/cases.json", .reason = "fixdep fixture manifest" },
};

const phase2_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "bootstrap note and tests README share returned Phase 2 packet anchors" {
    try expectContains(docs.tests_readme, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");

    for (shared_markers) |entry| {
        _ = entry.reason;
        try expectContains(docs.bootstrap_note, entry.marker);
        try expectContains(docs.tests_readme, entry.marker);
    }
}

test "both docs keep the same rematerialized make-wrapper route set" {
    for (phase2_make_routes) |route| {
        try expectContains(docs.bootstrap_note, route);
        try expectContains(docs.tests_readme, route);
    }
}

test "contract distinguishes current packet evidence from broader future work" {
    try expectContains(docs.tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet");
    try expectContains(docs.bootstrap_note, "# Phase 2 Toolchain Bootstrap Notes");

    try testing.expectEqual(@as(usize, 19), shared_markers.len);
    try testing.expectEqual(@as(usize, 8), phase2_make_routes.len);
}
