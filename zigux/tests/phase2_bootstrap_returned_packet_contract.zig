const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 22));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "bootstrap note keeps the returned Phase 2 packet present, not missing" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(note);

    try expectContains(note, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.");
    try expectContains(note, "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.");
    try expectContains(note, "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit");
    try expectContains(note, "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit");
    try expectContains(note, "`make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`");
}

test "policy, workflow, and make routes back the bootstrap-note packet" {
    const policy = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const makefile = try readRepoFile(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-fixdep\"");
    try expectContains(policy, "\"phase2-validate\"");

    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(workflow, "make -C zigux phase2-toolchain");
    try expectContains(workflow, "make -C zigux phase2-fixdep");
    try expectContains(workflow, "make -C zigux phase2-cross");
    try expectContains(workflow, "make -C zigux phase2");

    try expectContains(makefile, "phase2-toolchain:");
    try expectContains(makefile, "phase2-cross:");
    try expectContains(makefile, "phase2-fixdep: phase2-toolchain");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectContains(makefile, "$(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py");
}

test "direct cross and fixdep fixtures keep the returned packet reviewable" {
    const cross_targets = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(cross_targets);
    const fixdep_cases = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/fixdep/cases.json");
    defer std.testing.allocator.free(fixdep_cases);
    const fixdep = try readRepoFile(std.testing.allocator, "scripts/zigux/fixdep.zig");
    defer std.testing.allocator.free(fixdep);

    try expectContains(cross_targets, "\"target\": \"x86_64-linux\"");
    try expectContains(cross_targets, "\"target\": \"aarch64-linux\"");
    try expectContains(cross_targets, "\"validation_mode\": \"archive_required\"");
    try expectContains(cross_targets, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(cross_targets, "\"target\""));

    try std.testing.expectEqual(@as(usize, 13), countOccurrences(fixdep_cases, "\"name\""));
    try expectContains(fixdep_cases, "\"name\": \"sample_double_backslash_comment\"");
    try expectContains(fixdep_cases, "\"name\": \"sample_missing_dep_stdout_full\"");
    try expectContains(fixdep_cases, "\"name\": \"sample_output_write\"");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixdep_cases, "\"stdout_mode\": \"dev_full\""));

    try expectContains(fixdep, "test \"config parsing stops at the first embedded NUL\"");
    try expectContains(fixdep, "test \"open dependency file classification keeps PermissionDenied on the C-style path\"");
    try expectContains(fixdep, "test \"escaped colon dependency survives concatenated target CRLF comment path\"");
}
