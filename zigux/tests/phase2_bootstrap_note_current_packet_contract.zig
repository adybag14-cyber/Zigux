const std = @import("std");

const max_file_size = 512 * 1024;

const bootstrap_note = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const current_packet_markers = [_][]const u8{
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
};

const workflow_commands = [_][]const u8{
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "zig test scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/fixdep.zig",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 bootstrap note keeps current direct packet explicit" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, bootstrap_note);
    defer allocator.free(note);

    try expectContains(note, "# Phase 2 Toolchain Bootstrap Notes");
    try expectContains(note, "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.");
    try expectContains(note, "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.758+748e7c5e3`");
    try expectContains(note, "names `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate` as the required Linux-style make routes");
    for (current_packet_markers) |marker| try expectContains(note, marker);
    try expectContains(note, "`scripts/zigux/artifact_diff.py` is directly readable on current `master`");
    try expectContains(note, "`third_party/README.md` is directly readable on current `master`");
    try expectContains(note, "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit");
    try expectContains(note, "pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane");
}

test "phase2 bootstrap note agrees with policy archive and closure companions" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, bootstrap_note);
    defer allocator.free(note);
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const archive_readme = try readRepoFile(allocator, "third_party/README.md");
    defer allocator.free(archive_readme);
    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);

    const channel = "0.17.0-dev.758+748e7c5e3";
    const archive_path = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
    const archive_sha = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
    for ([_][]const u8{ note, policy, archive_readme }) |surface| {
        try expectContains(surface, channel);
        try expectContains(surface, archive_sha);
    }
    try expectContains(note, archive_path);
    try expectContains(archive_readme, archive_path);
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(manifest, "\"Documentation/zigux/phase2-toolchain-bootstrap-notes.md\"");
    try expectContains(manifest, "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"");
    try expectContains(manifest, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-cross.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(closure, "shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(closure, "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(scripts_readme, "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`");
}

test "phase2 bootstrap note keeps workflow replay and follow-through boundary bounded" {
    const allocator = std.testing.allocator;
    const note = try readRepoFile(allocator, bootstrap_note);
    defer allocator.free(note);
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const review_checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);

    for (workflow_commands) |command| {
        try expectContains(note, command);
        try expectContains(workflow, command);
    }
    try expectBefore(note, "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`", "`make -C zigux phase2-toolchain`");
    try expectBefore(note, "`make -C zigux phase2-toolchain`", "`make -C zigux phase2`");
    try expectContains(tests_readme, bootstrap_note);
    try expectContains(review_checklist, bootstrap_note);
    try expectContains(review_checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(note, "Do not widen this note into genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims");
    try expectContains(note, "Keep future Phase 2 follow-up inside one current packet surface at a time");
    try expectAbsent(note, "Treat older validator-first-only Phase 2 names as current repo-reality gaps");
}
