const std = @import("std");
const testing = std.testing;

const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const makefile_path = "zigux/Makefile";
const validator_path = "scripts/zigux/validate-phase2-closure.py";

const phase2_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const make_targets = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
};

const closure_validators = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

const expected_route_line =
    "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2";

const expected_validator_line =
    "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try testing.expectEqual(@as(usize, 1), count);
}

fn expectJsonStringContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var quoted: [128]u8 = undefined;
    try testing.expect(needle.len + 2 <= quoted.len);
    quoted[0] = '"';
    @memcpy(quoted[1 .. needle.len + 1], needle);
    quoted[needle.len + 1] = '"';
    try expectContainsOnce(haystack, quoted[0 .. needle.len + 2]);
}

fn expectLineContainsOnce(haystack: []const u8, line: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, " \t\r"), line)) {
            count += 1;
        }
    }
    try testing.expectEqual(@as(usize, 1), count);
}

test "closure note keeps the shared Phase 2 make routes explicit" {
    const closure = try readFile(testing.allocator, closure_path);
    defer testing.allocator.free(closure);

    try expectContains(closure, expected_route_line);
    try expectContains(closure, expected_validator_line);

    for (phase2_routes) |route| {
        try expectContains(closure, route);
    }
    for (closure_validators) |command| {
        try expectContains(closure, command);
    }
}

test "tool manifest make_wrappers mirrors the closure route packet" {
    const manifest = try readFile(testing.allocator, manifest_path);
    defer testing.allocator.free(manifest);

    try expectContains(manifest, "\"make_wrappers\"");
    try expectContains(manifest, "\"zigux/Makefile\"");
    for (phase2_routes) |route| {
        try expectJsonStringContainsOnce(manifest, route);
    }
}

test "Makefile exposes the routes that the closure packet advertises" {
    const makefile = try readFile(testing.allocator, makefile_path);
    defer testing.allocator.free(makefile);

    for (make_targets) |target| {
        try expectLineContainsOnce(makefile, target);
    }

    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
}

test "closure validator derives and checks the same make-route packet" {
    const validator = try readFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator);

    try expectContains(validator, "expected_routes = [");
    try expectContains(validator, "manifest_surface_values[\"make_wrappers\"]");
    try expectContains(validator, "value.startswith(\"make -C \")");
    try expectContains(validator, "expected_routes_line = \"PHASE2_SHARED_MAKE_ROUTES=\" + \",\".join(expected_routes)");
    try expectContains(validator, "expected_makefile_lines = (");
    try expectContains(validator, "MISSING_MAKEFILE_LINE");
    try expectContains(validator, "DUPLICATE_MAKEFILE_LINE");
}
