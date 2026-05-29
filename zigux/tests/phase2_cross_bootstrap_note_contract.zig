const std = @import("std");

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "bootstrap note keeps current direct cross packet visible" {
    const bootstrap_notes = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(bootstrap_notes);

    try expectContains(bootstrap_notes, "scripts/zigux/check-phase2-cross.py");
    try expectContains(bootstrap_notes, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(bootstrap_notes, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(bootstrap_notes, "make -C zigux phase2-cross");
    try expectContains(bootstrap_notes, "x86_64-linux");
    try expectContains(bootstrap_notes, "aarch64-linux");
    try expectContains(bootstrap_notes, "archive_required");
    try expectContains(bootstrap_notes, "route_contract_only");
    try expectContains(bootstrap_notes, "No current repo-reality gaps remain inside the bounded toolchain");
}

test "cross fixture and policy agree on archive scope and route target split" {
    const policy = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);
    const cross_targets = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(cross_targets);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\"");

    try expectContains(cross_targets, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(cross_targets, "\"target\": \"x86_64-linux\"");
    try expectContains(cross_targets, "\"validation_mode\": \"archive_required\"");
    try expectContains(cross_targets, "\"target\": \"aarch64-linux\"");
    try expectContains(cross_targets, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, cross_targets, "\"target\":"));
}

test "workflow and Makefile keep the cross replay route wired" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const makefile = try readRepoFile(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    try expectContains(workflow, "Self-test current Phase 2 cross checker");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(workflow, "Check current Phase 2 direct cross-route packet");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-cross.py");
    try expectContains(workflow, "Self-test current Phase 2 cross selftest alignment checker");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(workflow, "Run current Phase 2 cross make route");
    try expectContains(workflow, "make -C zigux phase2-cross");

    try expectContains(makefile, "phase2-cross:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}
