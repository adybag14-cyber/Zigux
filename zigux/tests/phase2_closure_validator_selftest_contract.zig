const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

const validator_selftest_markers = [_][]const u8{
    "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in contract checks\")",
    "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass",
    "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}",
    "UNEXPECTED_MANIFEST_GAPS",
    "MISSING_MANIFEST_SURFACE",
    "MISSING_CLOSURE_LINE",
    "MISSING_CLOSURE_MARKER",
    "MISSING_WORKFLOW_LINE",
    "MISSING_MAKEFILE_LINE",
};

const closure_success_markers = [_][]const u8{
    "PHASE2_CLOSURE_VALIDATION=pass",
    "PHASE2_CLOSURE_STATUS=parked",
    "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure",
    "PHASE2_CLOSURE_REMAINING_GAPS=",
};

const closure_validator_line =
    "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py";

test "phase 2 closure validator keeps self-test fail-closed coverage explicit" {
    const validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 256 * 1024);
    defer std.testing.allocator.free(validator);

    for (validator_selftest_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectBefore(
        validator,
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass",
        "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}",
    );
    try expectBefore(validator, "UNEXPECTED_MANIFEST_GAPS", "MISSING_CLOSURE_LINE");
    try expectAbsent(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CHECK_COUNT");
}

test "phase 2 closure validator advertises the parked success packet" {
    const validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 256 * 1024);
    defer std.testing.allocator.free(validator);

    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    for (closure_success_markers) |marker| {
        try expectContains(validator, marker);
    }

    try expectContains(validator, closure_validator_line);
    try expectContains(closure_note, closure_validator_line);
    try expectContains(closure_note, "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`");
    try expectContains(closure_note, "`PHASE2_STATUS=parked`");
    try expectAbsent(closure_note, "`PHASE2_STATUS=closed`");
}

test "workflow and makefile run closure self-test before live closure check" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 1024 * 1024);
    defer std.testing.allocator.free(workflow);

    const makefile = try readRepoFile("zigux/Makefile", 256 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n",
        "        run: python3 scripts/zigux/validate-phase2-closure.py\n",
    );
    try expectExactCount(
        workflow,
        "        run: python3 scripts/zigux/validate-phase2-closure.py --self-test\n",
        1,
    );
    try expectExactCount(
        workflow,
        "        run: python3 scripts/zigux/validate-phase2-closure.py\n",
        1,
    );
    try expectBefore(
        workflow,
        "        run: make -C zigux phase2-validate\n",
        "        run: make -C zigux phase2\n",
    );

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
    try expectBefore(
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    );
    try expectContains(makefile, "phase2: phase2-validate");
}
