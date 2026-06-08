const std = @import("std");

const repo_paths = struct {
    const workflow = ".github/workflows/zigux-bootstrap.yml";
    const makefile = "zigux/Makefile";
    const direct_checker = "scripts/zigux/check-phase2-cross.py";
    const alignment_checker = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
    const fixture = "zigux/tests/fixtures/phase2_cross_targets.json";
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try indexOfRequired(haystack, earlier);
    const later_index = try indexOfRequired(haystack, later);
    try std.testing.expect(earlier_index < later_index);
}

fn expectExactLine(text: []const u8, marker: []const u8) !void {
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, marker)) return;
    }
    std.debug.print("missing exact line: {s}\n", .{marker});
    return error.MissingExactLine;
}

test "bootstrap concurrency keeps master runs exact-head and preserves PR cancellation" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);

    try expectExactLine(workflow, "concurrency:");
    try expectExactLine(workflow, "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}");
    try expectExactLine(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try expectContains(workflow, "Run every master push so exact-head bootstrap status stays attached");

    try expectBefore(workflow, "concurrency:", "jobs:");
    try expectBefore(workflow, "format('{0}-{1}', github.workflow, github.sha)", "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
}

test "pull request path filters cover every cross-matrix source family" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);

    try expectExactLine(workflow, "pull_request:");
    try expectExactLine(workflow, "paths:");
    try expectExactLine(workflow, "- 'scripts/zigux/**'");
    try expectExactLine(workflow, "- 'zigux/**'");
    try expectExactLine(workflow, "- 'third_party/**'");
    try expectExactLine(workflow, "- '.github/workflows/zigux-bootstrap.yml'");

    try expectBefore(workflow, "- 'scripts/zigux/**'", "- 'third_party/**'");
    try expectBefore(workflow, "- 'third_party/**'", "- 'zigux/**'");
    try expectBefore(workflow, "- 'zigux/**'", "workflow_dispatch:");
}

test "workflow and Makefile keep direct cross checks on the same route boundary" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);
    const makefile = try readFile(allocator, repo_paths.makefile);
    defer allocator.free(makefile);

    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross.py");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectExactLine(workflow, "run: make -C zigux phase2-cross");

    try expectExactLine(makefile, "phase2-cross:");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");

    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test", "run: make -C zigux phase2-cross");
    try expectBefore(makefile, "phase2-cross:", "phase2-genksyms: phase2-toolchain");
}

test "triggered cross files still expose the two-target fixture boundary" {
    const allocator = std.testing.allocator;
    const direct_checker = try readFile(allocator, repo_paths.direct_checker);
    defer allocator.free(direct_checker);
    const alignment_checker = try readFile(allocator, repo_paths.alignment_checker);
    defer allocator.free(alignment_checker);
    const fixture = try readFile(allocator, repo_paths.fixture);
    defer allocator.free(fixture);

    try expectContains(direct_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(direct_checker, "ROUTE = \"make -C zigux phase2-cross\"");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(alignment_checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(alignment_checker, "PHASE2_CROSS_ALIGNMENT=pass");

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
}
