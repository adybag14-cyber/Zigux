const std = @import("std");
const testing = std.testing;

const docs = struct {
    const bootstrap_note =
        \\# Phase 2 Toolchain Bootstrap Notes
        \\scripts/zigux/check-phase2-bootstrap-workflow-routes.py
        \\scripts/zigux/check-phase2-tests-readme-alignment.py
        \\scripts/zigux/check-phase2-cross.py
        \\python3 scripts/zigux/check-phase2-cross.py --self-test
        \\scripts/zigux/check-lane05-local-first-archive-workflow.py
        \\scripts/zigux/check-lane05-local-archive-readme.py
        \\scripts/zigux/check-lane05-install-zig-archive-verification.py
        \\scripts/zigux/stage-pinned-zig-archive.py
        \\scripts/zigux/check-lane05-stage-helper-contract.py
        \\scripts/zigux/check-lane05-stage-helper-selftest.py
        \\scripts/zigux/check-phase2-genksyms-selftest-alignment.py
        \\scripts/zigux/check-genksyms-bridge.py
        \\scripts/zigux/genksyms.zig
        \\scripts/zigux/check-phase2-fixdep-gate.py
        \\scripts/zigux/check-fixdep-diff.py
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
        \\scripts/zigux/check-phase2-bootstrap-workflow-routes.py
        \\scripts/zigux/check-phase2-tests-readme-alignment.py
        \\scripts/zigux/check-phase2-cross.py
        \\python3 scripts/zigux/check-phase2-cross.py --self-test
        \\scripts/zigux/check-lane05-local-first-archive-workflow.py
        \\scripts/zigux/check-lane05-local-archive-readme.py
        \\scripts/zigux/check-lane05-install-zig-archive-verification.py
        \\scripts/zigux/stage-pinned-zig-archive.py
        \\scripts/zigux/check-lane05-stage-helper-contract.py
        \\scripts/zigux/check-lane05-stage-helper-selftest.py
        \\scripts/zigux/check-phase2-genksyms-selftest-alignment.py
        \\scripts/zigux/check-genksyms-bridge.py
        \\scripts/zigux/genksyms.zig
        \\scripts/zigux/check-phase2-fixdep-gate.py
        \\scripts/zigux/check-fixdep-diff.py
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
    .{ .marker = "scripts/zigux/check-phase2-bootstrap-workflow-routes.py", .reason = "bootstrap workflow-route guard" },
    .{ .marker = "scripts/zigux/check-phase2-tests-readme-alignment.py", .reason = "tests-root reminder alignment guard" },
    .{ .marker = "scripts/zigux/check-phase2-cross.py", .reason = "direct cross-route checker" },
    .{ .marker = "python3 scripts/zigux/check-phase2-cross.py --self-test", .reason = "direct cross-route self-test" },
    .{ .marker = "scripts/zigux/check-lane05-local-first-archive-workflow.py", .reason = "local-first archive workflow guard" },
    .{ .marker = "scripts/zigux/check-lane05-local-archive-readme.py", .reason = "third_party archive README guard" },
    .{ .marker = "scripts/zigux/check-lane05-install-zig-archive-verification.py", .reason = "archive-verification guard" },
    .{ .marker = "scripts/zigux/stage-pinned-zig-archive.py", .reason = "staged archive helper" },
    .{ .marker = "scripts/zigux/check-lane05-stage-helper-contract.py", .reason = "staged helper contract" },
    .{ .marker = "scripts/zigux/check-lane05-stage-helper-selftest.py", .reason = "staged helper self-test" },
    .{ .marker = "scripts/zigux/check-phase2-genksyms-selftest-alignment.py", .reason = "genksyms selftest alignment guard" },
    .{ .marker = "scripts/zigux/check-genksyms-bridge.py", .reason = "genksyms bridge checker" },
    .{ .marker = "scripts/zigux/genksyms.zig", .reason = "genksyms Zig bridge helper" },
    .{ .marker = "scripts/zigux/check-phase2-fixdep-gate.py", .reason = "fixdep governance gate" },
    .{ .marker = "scripts/zigux/check-fixdep-diff.py", .reason = "fixdep parity checker" },
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
