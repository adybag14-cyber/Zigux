const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(768 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "toolchain owner map keeps shared and tool-local lanes split" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer allocator.free(note);

    try expectContains(note, "# Phase 2 Toolchain Lane Sequencing");
    try expectContains(note, "shared sequencing lane `P2-Y10` owns only shared Phase 2 toolchain reminder and anti-overlap work");
    try expectContains(note, "shared backlog truthfulness lane `P2-Y12` owns turning current cross-family backlog evidence into one bounded next-safe-step correction");
    try expectContains(note, "Makefile toolchain lane `P2-X09` owns the repo-local `.zig-toolchain` fallback");
    try expectContains(note, "fixdep route-governance lane `P2-Y01` owns fixdep gate-marker and route-inventory wording");
    try expectContains(note, "fixdep closure lane `P2-Y02` owns bounded next-step or closure truthfulness");
    try expectContains(note, "genksyms roadmap-survey lane `P2-L07` owns repo-versus-roadmap evidence");
    try expectContains(note, "genksyms note-truthfulness lane `P2-L12` owns same-family survey or closure wording corrections");
    try expectContains(note, "genksyms fixture lane `P2-L10` owns bounded genksyms bridge fixture and expected-output drift");
    try expectContains(note, "genksyms gate lane `P2-L11` owns workflow-backed replay or validator wiring");
    try expectContains(note, "kconfig bridge behavior lane `P2-X05` owns `scripts/zigux/kconfig/conf_bridge.zig` behavior follow-up");
    try expectContains(note, "kconfig bridge checker parity lane `P2-L18` owns the current `conf_bridge` checker-and-manifest helper-anchor parity");
    try expectContains(note, "confdata survey lane `P2-L19` stays parked as the scaffold-closed survey note");
    try expectContains(note, "confdata checker lane `P2-Y07` owns current checker-underflow repair");
    try expectContains(note, "confdata bridge truthfulness lane `P2-L24` owns malformed-quote and helper-anchor follow-through");
}

test "owner map stays paired with current shared packet evidence" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer allocator.free(note);
    const bootstrap = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap);
    const review = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review);
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(note, "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(note, "`zigux/tests/fixtures/phase2_tool_manifest.json`");
    try expectContains(note, "`zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectContains(note, "`scripts/zigux/check-phase2-tool-manifest.py`");
    try expectContains(note, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectMissing(note, "`scripts/zigux/check-phase2-tool-manifest-packets.py`");
    try expectMissing(note, "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`");

    try expectContains(bootstrap, "`scripts/zigux/check-phase2-tool-manifest.py`");
    try expectContains(bootstrap, "`scripts/zigux/check-phase2-docs-shared-reminder.py`");
    try expectContains(review, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tool-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
}

test "current backlog evidence parks shared sequencing unless a broad surface drifts" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer allocator.free(note);

    try expectContains(note, "current `master` already carries the separate genksyms dual-implementation survey, conf bridge survey, confdata survey, fixdep next-step note");
    try expectContains(note, "the remaining shared correction path is therefore narrower than a fresh sequencing-note rewrite");
    try expectContains(note, "reopen `P2-Y10` only for multi-family route, manifest, validator, or reminder-surface drift");
    try expectContains(note, "reopen `P2-Y12` only when a shared backlog note points at the wrong next safe Phase 2 follow-through");
    try expectContains(note, "tool-local behavior, fixture, checker, and gate work should continue to stay in the dedicated fixdep, genksyms, conf bridge, and confdata lanes");
    try expectBefore(note, "## Current Backlog Evidence", "## Shared Packet Surfaces");
}

test "sequencing rules keep make routes shared and behavior work local" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-lane-sequencing.md");
    defer allocator.free(note);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const routes = [_][]const u8{
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    };

    inline for (routes) |route| {
        try expectContains(note, route);
    }
    try expectContains(makefile, "phase2-toolchain");
    try expectContains(makefile, "phase2-tools");
    try expectContains(makefile, "phase2-kconfig");
    try expectContains(makefile, "phase2-cross");
    try expectContains(makefile, "phase2-genksyms");
    try expectContains(makefile, "phase2-fixdep");
    try expectContains(makefile, "phase2-validate");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");

    try expectContains(note, "Prefer one Phase 2 lane at a time");
    try expectContains(note, "If only one tool family drifts on current `master`, stay inside that tool family's lane");
    try expectContains(note, "Do not use this note to revive already-closed `confdata` scaffolding");
    try expectContains(note, "collapse the four-way genksyms split back into one generic packet");
}
