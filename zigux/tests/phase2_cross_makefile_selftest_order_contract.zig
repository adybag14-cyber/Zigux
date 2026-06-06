const std = @import("std");

const makefile_path = "zigux/Makefile";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const makefile_phase2_cross_target = "phase2-cross:";
const makefile_direct_selftest = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test";
const makefile_direct_check = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py";
const makefile_alignment_selftest = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test";
const makefile_alignment_check = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py";

const workflow_direct_selftest = "run: python3 scripts/zigux/check-phase2-cross.py --self-test";
const workflow_direct_check = "run: python3 scripts/zigux/check-phase2-cross.py";
const workflow_alignment_selftest = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test";
const workflow_alignment_check = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py";
const workflow_make_route = "run: make -C zigux phase2-cross";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn trimmedLineEquals(line: []const u8, expected: []const u8) bool {
    return std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), expected);
}

fn countExactTrimmedLines(text: []const u8, expected: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (trimmedLineEquals(line, expected)) count += 1;
    }
    return count;
}

fn findExactTrimmedLine(text: []const u8, expected: []const u8) !usize {
    var lines = std.mem.splitScalar(u8, text, '\n');
    var index: usize = 0;
    while (lines.next()) |line| : (index += 1) {
        if (trimmedLineEquals(line, expected)) return index;
    }
    return error.TestUnexpectedResult;
}

fn expectSingleLine(text: []const u8, expected: []const u8) !usize {
    try std.testing.expectEqual(@as(usize, 1), countExactTrimmedLines(text, expected));
    return try findExactTrimmedLine(text, expected);
}

fn expectAscending(indices: []const usize) !void {
    var previous = indices[0];
    for (indices[1..]) |index| {
        try std.testing.expect(previous < index);
        previous = index;
    }
}

test "phase2-cross Makefile route runs direct and alignment self-tests before live checks" {
    const makefile = try readRepoFile(makefile_path, 96 * 1024);
    defer std.testing.allocator.free(makefile);

    const target_index = try expectSingleLine(makefile, makefile_phase2_cross_target);
    const direct_selftest_index = try expectSingleLine(makefile, makefile_direct_selftest);
    const direct_check_index = try expectSingleLine(makefile, makefile_direct_check);
    const alignment_selftest_index = try expectSingleLine(makefile, makefile_alignment_selftest);
    const alignment_check_index = try expectSingleLine(makefile, makefile_alignment_check);

    try expectAscending(&.{
        target_index,
        direct_selftest_index,
        direct_check_index,
        alignment_selftest_index,
        alignment_check_index,
    });
}

test "bootstrap workflow keeps the same phase2-cross self-test then check sequence" {
    const workflow = try readRepoFile(workflow_path, 256 * 1024);
    defer std.testing.allocator.free(workflow);

    const direct_selftest_index = try expectSingleLine(workflow, workflow_direct_selftest);
    const direct_check_index = try expectSingleLine(workflow, workflow_direct_check);
    const alignment_selftest_index = try expectSingleLine(workflow, workflow_alignment_selftest);
    const alignment_check_index = try expectSingleLine(workflow, workflow_alignment_check);
    const make_route_index = try expectSingleLine(workflow, workflow_make_route);

    try expectAscending(&.{
        direct_selftest_index,
        direct_check_index,
        alignment_selftest_index,
        alignment_check_index,
        make_route_index,
    });
}

test "phase2-cross route remains inside the Phase 2 aggregate dependency chain" {
    const makefile = try readRepoFile(makefile_path, 96 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");
    try expectContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
}
