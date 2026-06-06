const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const makefile_path = "zigux/Makefile";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const aggregate_validator = "python3 scripts/zigux/validate-phase2.py";
const closure_validator = "python3 scripts/zigux/validate-phase2-closure.py";
const validators_marker =
    "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py";

test "phase2 closure note keeps validator pair explicit after shared replay routes" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const closure = try readRepoFile(arena.allocator(), closure_path);

    try expectContains(closure, "- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(closure, validators_marker);
    try expectOrdered(closure, "## Shared Replay Routes", validators_marker);
    try expectOrdered(closure, validators_marker, "## Repo-Reality Gaps");
    try expectOrdered(closure, "`PHASE2_STATUS=parked`", validators_marker);
}

test "phase2 tool manifest mirrors closure validator authority" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const manifest = try readRepoFile(arena.allocator(), manifest_path);

    try expectContains(manifest, "\"validators\": [");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectOrdered(manifest, "\"validators\": [", "\"scripts/zigux/validate-phase2.py\"");
    try expectOrdered(manifest, "\"scripts/zigux/validate-phase2.py\"", "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "Keep the directly readable validator pair explicit");
}

test "makefile routes aggregate validation before closure-specific validation" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const makefile = try readRepoFile(arena.allocator(), makefile_path);

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectOrdered(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectOrdered(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py", "phase2: phase2-validate");
}

test "bootstrap workflow runs closure validator after aggregate phase2 replay" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const workflow = try readRepoFile(arena.allocator(), workflow_path);

    try expectContains(workflow, "name: Run current Phase 2 aggregate make route");
    try expectContains(workflow, "run: make -C zigux phase2");
    try expectContains(workflow, "name: Validate current Phase 2 tool packet");
    try expectContains(workflow, "run: python3 scripts/zigux/validate-phase2.py");
    try expectContains(workflow, "name: Self-test current Phase 2 closure validator");
    try expectContains(workflow, "run: python3 scripts/zigux/validate-phase2-closure.py --self-test");
    try expectContains(workflow, "name: Check current Phase 2 closure packet");
    try expectContains(workflow, "run: python3 scripts/zigux/validate-phase2-closure.py");
    try expectOrdered(workflow, "run: make -C zigux phase2", "run: python3 scripts/zigux/validate-phase2.py");
    try expectOrdered(workflow, "name: Validate current Phase 2 tool packet", "name: Self-test current Phase 2 closure validator");
    try expectOrdered(workflow, "name: Self-test current Phase 2 closure validator", "name: Check current Phase 2 closure packet");
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
