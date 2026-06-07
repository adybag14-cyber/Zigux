const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLineOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

test "phase2 closure note and manifest keep fixdep support explicit" {
    const allocator = std.testing.allocator;

    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    try expectContains(closure, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure, "`scripts/zigux/check-fixdep-diff.py`");
    try expectContains(closure, "`make -C zigux phase2-fixdep`");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    const manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"fixdep_support\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(manifest, "\"scripts/zigux/fixdep.zig\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/fixdep/cases.json\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/fixdep/sample_multi_target.d\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/fixdep/shared#config.h\"");
}

test "closure validator preserves fixdep in shared tooling derivation" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase2-closure.py");
    defer allocator.free(validator);

    try expectContains(validator, "SHARED_TOOLING_COMMANDS = (");
    try expectContains(validator, "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (");
    try expectContains(validator, "MANIFEST_SURFACE_KEYS = (");
    try expectContains(validator, "\"python3 scripts/zigux/check-phase2-fixdep-gate.py\",");
    try expectContains(validator, "\"python3 scripts/zigux/check-fixdep-diff.py\",");
    try expectContains(validator, "\"make -C zigux phase2-fixdep\",");
    try expectContains(validator, "expected_shared_tooling_line = \"PHASE2_SHARED_TOOLING_CHECKERS=\"");
    try expectContains(validator, "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\"");
}

test "fixdep gate and make route keep the same closure packet" {
    const allocator = std.testing.allocator;

    const gate = try readRepoFile(allocator, "scripts/zigux/check-phase2-fixdep-gate.py");
    defer allocator.free(gate);
    try expectContains(gate, "REQUIRED_FIXDEP_CASE_NAMES = (");
    try expectContains(gate, "\"sample_multi_target\",");
    try expectContains(gate, "\"sample_output_write\",");
    try expectContains(gate, "REQUIRED_FIXDEP_EXPECTED_FIXTURE_FILES = (");
    try expectContains(gate, "\"sample_output_write_expected.stderr.txt\",");
    try expectContains(gate, "PHASE2_FIXDEP_GATE_REQUIRED_EXPECTED_FIXTURE_COUNT=");
    try expectContains(gate, "PHASE2_FIXDEP_GATE_REQUIRED_DIFF_SELF_TEST_CASE_COUNT=");

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    try expectLineOnce(makefile, "phase2-fixdep: phase2-toolchain");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --zig \"$(ZIG_REPO_ROOT)\"");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig");
    try expectLineOnce(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}
