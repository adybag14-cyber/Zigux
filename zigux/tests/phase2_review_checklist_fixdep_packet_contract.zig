const std = @import("std");

const max_file_size = 6 * 1024 * 1024;

const REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md";
const DOCS_ROOT = "Documentation/zigux/README.md";
const CLOSURE_NOTE = "Documentation/zigux/phase2-closure.md";
const SCRIPTS_README = "scripts/zigux/README.md";
const TESTS_README = "zigux/tests/README.md";
const FIXDEP_GATE = "scripts/zigux/check-phase2-fixdep-gate.py";
const FIXDEP_CASES = "zigux/tests/fixtures/fixdep/cases.json";
const MAKEFILE = "zigux/Makefile";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) {
        std.debug.print("missing marker: {s}\n", .{marker});
        return error.MissingMarker;
    }
}

fn expectBefore(text: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, text, first) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, text, second) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

test "review checklist keeps the Phase 2 fixdep packet explicit" {
    const allocator = std.testing.allocator;
    const checklist = try readFile(allocator, REVIEW_CHECKLIST);
    defer allocator.free(checklist);

    try expectContains(checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(checklist, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(checklist, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(checklist, "`scripts/zigux/fixdep.zig`");
    try expectContains(checklist, "`zigux/tests/fixtures/fixdep/cases.json`");
    try expectContains(checklist, "`make -C zigux phase2-fixdep`");
    try expectContains(checklist, "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`");
    try expectContains(checklist, "`python3 scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(checklist, "`python3 scripts/zigux/check-fixdep-diff.py --self-test`");
    try expectContains(checklist, "`python3 scripts/zigux/check-fixdep-diff.py`");
    try expectContains(checklist, "`zig test scripts/zigux/fixdep.zig`");
}

test "shared documentation surfaces agree on the returned fixdep lane" {
    const allocator = std.testing.allocator;
    const docs_root = try readFile(allocator, DOCS_ROOT);
    defer allocator.free(docs_root);
    const closure = try readFile(allocator, CLOSURE_NOTE);
    defer allocator.free(closure);
    const scripts = try readFile(allocator, SCRIPTS_README);
    defer allocator.free(scripts);
    const tests_readme = try readFile(allocator, TESTS_README);
    defer allocator.free(tests_readme);

    const shared_markers = [_][]const u8{
        "`scripts/zigux/check-phase2-fixdep-gate.py`",
        "`scripts/zigux/check-fixdep-diff.py`",
        "`scripts/zigux/fixdep.zig`",
        "`zigux/tests/fixtures/fixdep/cases.json`",
        "`make -C zigux phase2-fixdep`",
    };

    for (shared_markers) |marker| {
        try expectContains(docs_root, marker);
        try expectContains(scripts, marker);
        try expectContains(tests_readme, marker);
    }

    try expectContains(closure, "`Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`");
    try expectContains(closure, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(closure, "`make -C zigux phase2-fixdep`");
    try expectContains(
        scripts,
        "current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper",
    );
    try expectContains(
        tests_readme,
        "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`",
    );
}

test "fixdep gate fixture and wrapper route stay aligned with checklist wording" {
    const allocator = std.testing.allocator;
    const gate = try readFile(allocator, FIXDEP_GATE);
    defer allocator.free(gate);
    const cases = try readFile(allocator, FIXDEP_CASES);
    defer allocator.free(cases);
    const makefile = try readFile(allocator, MAKEFILE);
    defer allocator.free(makefile);

    try expectContains(gate, "REQUIRED_FIXDEP_CASE_NAMES = (");
    try expectContains(gate, "\"sample_escaped_colon\",");
    try expectContains(gate, "\"sample_double_backslash_comment\",");
    try expectContains(gate, "\"sample_output_write\",");
    try expectContains(gate, "PHASE2_FIXDEP_GATE_REQUIRED_FIXDEP_CASE_COUNT");

    try expectContains(cases, "\"name\": \"sample_escaped_colon\"");
    try expectContains(cases, "\"name\": \"sample_double_backslash_comment\"");
    try expectContains(cases, "\"name\": \"sample_output_write\"");

    try expectContains(makefile, "phase2-fixdep: phase2-toolchain");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig");
    try expectBefore(makefile, "phase2-fixdep: phase2-toolchain", "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}
