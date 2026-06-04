const std = @import("std");
const testing = std.testing;

const validator_commands = [_][]const u8{
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
};

fn readText(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireExactOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try testing.expectEqual(@as(usize, 1), count);
}

fn joinedLine(comptime prefix: []const u8, comptime values: []const []const u8) []const u8 {
    comptime {
        var line: []const u8 = prefix;
        for (values, 0..) |value, index| {
            if (index != 0) line = line ++ ",";
            line = line ++ value;
        }
        return line;
    }
}

const expected_validator_line = joinedLine(
    "PHASE2_CLOSURE_VALIDATORS=",
    &validator_commands,
);

test "phase2 closure validator self-test guards manifest surface loss" {
    const validator = try readText("scripts/zigux/validate-phase2-closure.py");
    defer testing.allocator.free(validator);

    try requireContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass");
    try requireContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}");
    try requireContains(validator, "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");
    try requireContains(validator, "(root / \"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\").unlink()");
    try requireContains(validator, "\"MISSING_MANIFEST_SURFACE\"");
    try requireContains(validator, "\"UNEXPECTED_MANIFEST_GAPS\"");
    try requireContains(validator, "\"MISSING_CLOSURE_LINE\"");
    try requireContains(validator, "\"MISSING_CLOSURE_MARKER\"");
    try requireContains(validator, "manifest[\"repo_reality_gaps\"] = [\"drift\"]");
    try requireContains(
        validator,
        "in collect_issues(root)",
    );
}

test "phase2 closure validator pass output remains no-gap and parked" {
    const validator = try readText("scripts/zigux/validate-phase2-closure.py");
    defer testing.allocator.free(validator);

    try requireContains(validator, "PHASE2_CLOSURE_VALIDATION=pass");
    try requireContains(validator, "PHASE2_CLOSURE_STATUS=parked");
    try requireContains(validator, "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure");
    try requireContains(validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
    try requireExactOnce(validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
    try requireMissing(validator, "PHASE2_CLOSURE_REMAINING_GAPS=repo_reality_gap");
    try requireOrdered(
        validator,
        "if issues:",
        "print(\"PHASE2_CLOSURE_VALIDATION=pass\")",
    );
}

test "phase2 closure note, manifest, and workflow expose validator replay surfaces" {
    const closure = try readText("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);
    const manifest = try readText("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(manifest);
    const workflow = try readText(".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);
    const makefile = try readText("zigux/Makefile");
    defer testing.allocator.free(makefile);

    try requireContains(closure, expected_validator_line);
    try requireExactOnce(closure, expected_validator_line);
    for (validator_commands) |command| {
        try requireContains(closure, command);
    }
    try requireContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try requireContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try requireContains(manifest, "\"repo_reality_gaps\": []");

    try requireContains(workflow, "run: python3 scripts/zigux/validate-phase2.py\n");
    try requireContains(workflow, "run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n");
    try requireContains(workflow, "run: python3 scripts/zigux/validate-phase2-closure.py\n");
    try requireOrdered(
        workflow,
        "run: python3 scripts/zigux/validate-phase2.py\n",
        "run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
    );
    try requireOrdered(
        workflow,
        "run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n",
        "run: python3 scripts/zigux/validate-phase2-closure.py\n",
    );

    try requireOrdered(
        makefile,
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    );
    try requireMissing(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2-closure.py");
}
