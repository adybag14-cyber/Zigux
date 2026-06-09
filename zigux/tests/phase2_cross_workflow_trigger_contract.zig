const std = @import("std");

const repo_paths = struct {
    const workflow = ".github/workflows/zigux-bootstrap.yml";
    const makefile = "zigux/Makefile";
    const direct_checker = "scripts/zigux/check-phase2-cross.py";
    const alignment_checker = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
    const policy = "scripts/zigux/zig-toolchain-policy.json";
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

test "bootstrap workflow trigger keeps Phase 2 cross packet paths covered" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);

    try expectExactLine(workflow, "pull_request:");
    try expectExactLine(workflow, "paths:");
    try expectExactLine(workflow, "- 'scripts/zigux/**'");
    try expectExactLine(workflow, "- 'zigux/**'");
    try expectExactLine(workflow, "- 'third_party/**'");
    try expectExactLine(workflow, "- '.github/workflows/zigux-bootstrap.yml'");
    try expectContains(workflow, "Run every master push so exact-head bootstrap status stays attached");

    try expectBefore(workflow, "pull_request:", "permissions:");
    try expectBefore(workflow, "- 'scripts/zigux/**'", "workflow_dispatch:");
    try expectBefore(workflow, "- 'zigux/**'", "workflow_dispatch:");
}

test "workflow still runs direct and alignment cross checks before downstream Phase 2 routes" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, repo_paths.workflow);
    defer allocator.free(workflow);

    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross.py");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectExactLine(workflow, "run: make -C zigux phase2-cross");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test");
    try expectExactLine(workflow, "run: python3 scripts/zigux/check-phase2-required-make-routes.py");
    try expectExactLine(workflow, "run: make -C zigux phase2-validate");
    try expectExactLine(workflow, "run: make -C zigux phase2");

    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test", "run: python3 scripts/zigux/check-phase2-cross.py\n");
    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-cross.py\n", "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n", "run: make -C zigux phase2-cross");
    try expectBefore(workflow, "run: make -C zigux phase2-cross", "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test");
    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-required-make-routes.py\n", "run: make -C zigux phase2-validate");
    try expectBefore(workflow, "run: make -C zigux phase2-validate", "run: make -C zigux phase2\n");
}

test "Makefile route mirrors the workflow-visible cross packet" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, repo_paths.makefile);
    defer allocator.free(makefile);

    try expectExactLine(makefile, "phase2-cross:");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectExactLine(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
    try expectExactLine(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");

    try expectBefore(makefile, "phase2-cross:", "phase2-genksyms: phase2-toolchain");
    try expectBefore(makefile, "phase2-cross:", "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectBefore(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\n", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
}

test "triggered files expose the current x86 archive and aarch64 route-only boundary" {
    const allocator = std.testing.allocator;
    const direct_checker = try readFile(allocator, repo_paths.direct_checker);
    defer allocator.free(direct_checker);
    const alignment_checker = try readFile(allocator, repo_paths.alignment_checker);
    defer allocator.free(alignment_checker);
    const policy = try readFile(allocator, repo_paths.policy);
    defer allocator.free(policy);
    const fixture = try readFile(allocator, repo_paths.fixture);
    defer allocator.free(fixture);

    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT");
    try expectContains(direct_checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(alignment_checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(alignment_checker, "PHASE2_CROSS_ALIGNMENT=pass");

    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"");
    try expectContains(policy, "\"phase2-cross\"");

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
}
