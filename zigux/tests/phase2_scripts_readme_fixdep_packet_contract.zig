const std = @import("std");

const scripts_readme_path = "scripts/zigux/README.md";
const closure_path = "Documentation/zigux/phase2-closure.md";
const docs_readme_path = "Documentation/zigux/README.md";
const review_checklist_path = "Documentation/zigux/review-checklist.md";
const tests_readme_path = "zigux/tests/README.md";
const fixdep_gate_path = "scripts/zigux/check-phase2-fixdep-gate.py";
const fixdep_cases_path = "zigux/tests/fixtures/fixdep/cases.json";

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "scripts readme keeps returned fixdep packet explicit" {
    const scripts_readme = try readRepoFile(scripts_readme_path);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(scripts_readme, "Phase 2 flow - the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper");
    try expectContains(scripts_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(scripts_readme, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(scripts_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(scripts_readme, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-fixdep-diff.py --self-test`");
    try expectContains(scripts_readme, "`python3 scripts/zigux/check-fixdep-diff.py`");
    try expectContains(scripts_readme, "`zig test scripts/zigux/fixdep.zig`");
    try expectContains(scripts_readme, "`make -C zigux phase2-fixdep`");
    try expectOrder(scripts_readme, "Phase 2 flow - the current fixdep packet", "`make -C zigux phase2-fixdep`");
}

test "companion docs keep scripts-root fixdep packet aligned" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);
    const docs_readme = try readRepoFile(docs_readme_path);
    defer std.testing.allocator.free(docs_readme);
    const review_checklist = try readRepoFile(review_checklist_path);
    defer std.testing.allocator.free(review_checklist);
    const tests_readme = try readRepoFile(tests_readme_path);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(closure, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(closure, "`make -C zigux phase2-fixdep`");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(closure, "python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py");

    try expectContains(docs_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(docs_readme, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(docs_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(docs_readme, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(docs_readme, "`make -C zigux phase2-fixdep`");

    try expectContains(review_checklist, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(review_checklist, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(review_checklist, "`scripts/zigux/fixdep.zig`");
    try expectContains(review_checklist, "`zigux/tests/fixtures/fixdep/cases.json`");

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(tests_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(tests_readme, "`make -C zigux phase2-fixdep`");
}

test "fixdep checker and fixture roster match documented scripts-root packet" {
    const gate = try readRepoFile(fixdep_gate_path);
    defer std.testing.allocator.free(gate);
    const cases = try readRepoFile(fixdep_cases_path);
    defer std.testing.allocator.free(cases);

    try expectContains(gate, "FIXDEP_REL = Path(\"scripts/zigux/fixdep.zig\")");
    try expectContains(gate, "FIXDEP_DIFF_REL = Path(\"scripts/zigux/check-fixdep-diff.py\")");
    try expectContains(gate, "FIXDEP_CASES_REL = Path(\"zigux/tests/fixtures/fixdep/cases.json\")");
    try expectContains(gate, "SCRIPTS_README_REL = Path(\"scripts/zigux/README.md\")");
    try expectContains(gate, "EXPECTED_SELF_TEST_CASE_COUNT = 16");
    try expectContains(gate, "REQUIRED_FIXDEP_CASE_NAMES = (");
    try expectContains(gate, "\"phase2-fixdep: phase2-toolchain\",");
    try expectContains(gate, "\"run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\",");
    try expectContains(gate, "\"run: python3 scripts/zigux/check-fixdep-diff.py --self-test\",");
    try expectContains(gate, "\"run: zig test scripts/zigux/fixdep.zig\",");

    const expected_cases = [_][]const u8{
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

    for (expected_cases) |case_marker| {
        try expectContains(cases, case_marker);
    }

    try expectContains(cases, "\"stdout_mode\": \"dev_full\"");
    try expectAbsent(cases, "\"name\": \"sample_usage\"");
}
