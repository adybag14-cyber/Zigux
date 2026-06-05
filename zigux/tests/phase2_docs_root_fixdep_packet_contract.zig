const std = @import("std");

const allocator = std.testing.allocator;

const repo_files = .{
    .docs_readme = "Documentation/zigux/README.md",
    .phase2_closure = "Documentation/zigux/phase2-closure.md",
    .review_checklist = "Documentation/zigux/review-checklist.md",
    .scripts_readme = "scripts/zigux/README.md",
    .tests_readme = "zigux/tests/README.md",
    .fixdep_gate = "scripts/zigux/check-phase2-fixdep-gate.py",
    .fixdep_cases = "zigux/tests/fixtures/fixdep/cases.json",
};

fn readRepoFile(relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, relative_path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs root keeps the returned Phase 2 fixdep packet explicit" {
    const docs = try readRepoFile(repo_files.docs_readme);
    defer allocator.free(docs);

    try expectContains(docs, "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again");
    try expectContains(docs, "keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.");
    try expectContains(docs, "`make -C zigux phase2-fixdep`");
    try expectContains(docs, "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`");
}

test "shared reminder surfaces agree on the fixdep checker fixture and wrapper" {
    const closure = try readRepoFile(repo_files.phase2_closure);
    defer allocator.free(closure);
    const checklist = try readRepoFile(repo_files.review_checklist);
    defer allocator.free(checklist);
    const scripts = try readRepoFile(repo_files.scripts_readme);
    defer allocator.free(scripts);
    const tests_readme = try readRepoFile(repo_files.tests_readme);
    defer allocator.free(tests_readme);

    try expectContains(closure, "`Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`");
    try expectContains(closure, "`scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` keep the helper-local kconfig, direct cross-route, and fixdep governance/parity packet directly replayable beside the closure note.");
    try expectContains(closure, "`python3 scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure, "`python3 scripts/zigux/check-fixdep-diff.py`");
    try expectContains(closure, "`make -C zigux phase2-fixdep`");

    try expectContains(checklist, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(checklist, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(checklist, "`scripts/zigux/fixdep.zig`");
    try expectContains(checklist, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(checklist, "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet");

    try expectContains(scripts, "the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper");
    try expectContains(scripts, "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root");
    try expectContains(scripts, "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`");
    try expectContains(scripts, "`zig test scripts/zigux/fixdep.zig`");

    try expectContains(tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(tests_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(tests_readme, "`make -C zigux phase2-fixdep`");
    try expectContains(tests_readme, "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`");
}

test "fixdep checker and fixture keep the documented current roster" {
    const gate = try readRepoFile(repo_files.fixdep_gate);
    defer allocator.free(gate);
    const cases = try readRepoFile(repo_files.fixdep_cases);
    defer allocator.free(cases);

    try expectContains(gate, "\"scripts/zigux/check-phase2-fixdep-gate.py\",");
    try expectContains(gate, "\"scripts/zigux/check-fixdep-diff.py\",");
    try expectContains(gate, "\"scripts/zigux/fixdep.zig\",");
    try expectContains(gate, "\"zigux/tests/fixtures/fixdep/cases.json\",");
    try expectContains(gate, "\"phase2-fixdep: phase2-toolchain\",");
    try expectContains(gate, "\"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test\",");
    try expectContains(gate, "\"cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test\",");
    try expectContains(gate, "\"cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig\",");
    try expectContains(gate, "EXPECTED_SELF_TEST_CASE_COUNT = 16");

    const required_cases = [_][]const u8{
        "\"name\": \"sample\"",
        "\"name\": \"sample_multi_target\"",
        "\"name\": \"sample_escaped_space\"",
        "\"name\": \"sample_escaped_colon\"",
        "\"name\": \"sample_concatenated\"",
        "\"name\": \"sample_dependency_continuation\"",
        "\"name\": \"sample_comment_continuation\"",
        "\"name\": \"sample_double_backslash_comment\"",
        "\"name\": \"sample_comment_only\"",
        "\"name\": \"sample_comment_only_stdout_full\"",
        "\"name\": \"sample_missing_dep\"",
        "\"name\": \"sample_missing_dep_stdout_full\"",
        "\"name\": \"sample_output_write\"",
    };
    for (required_cases) |case_name| {
        try expectContains(cases, case_name);
    }

    try expectContains(cases, "\"expected_exit_code\": 0");
    try expectContains(cases, "\"expected_exit_code\": 1");
    try expectContains(cases, "\"expected_exit_code\": 2");
    try expectContains(cases, "\"stdout_mode\": \"dev_full\"");
    try expectNotContains(cases, "\"name\": \"sample_missing_dep_source_module\"");
}
