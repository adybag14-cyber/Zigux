const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const makefile_path = "zigux/Makefile";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const route = "make -C zigux phase2-cross";
const x86_target = "x86_64-linux";
const aarch64_target = "aarch64-linux";

const workflow_direct_selftest = "run: python3 scripts/zigux/check-phase2-cross.py --self-test";
const workflow_direct_check = "run: python3 scripts/zigux/check-phase2-cross.py";
const workflow_alignment_selftest = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test";
const workflow_alignment_check = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py";
const workflow_make_cross = "run: make -C zigux phase2-cross";
const workflow_required_routes_selftest = "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test";
const workflow_required_routes_check = "run: python3 scripts/zigux/check-phase2-required-make-routes.py";
const workflow_make_validate = "run: make -C zigux phase2-validate";
const workflow_make_phase2 = "run: make -C zigux phase2";

const makefile_cross_target = "phase2-cross:";
const makefile_direct_selftest = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test";
const makefile_direct_check = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py";
const makefile_alignment_selftest = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test";
const makefile_alignment_check = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py";
const makefile_validate_chain = "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep";
const makefile_phase2_chain = "phase2: phase2-validate";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
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

fn expectSingleTrimmedLine(text: []const u8, expected: []const u8) !usize {
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "bootstrap workflow keeps the cross make route after direct and alignment checks" {
    const workflow = try readRepoFile(workflow_path, 256 * 1024);
    defer std.testing.allocator.free(workflow);

    const direct_selftest_index = try expectSingleTrimmedLine(workflow, workflow_direct_selftest);
    const direct_check_index = try expectSingleTrimmedLine(workflow, workflow_direct_check);
    const alignment_selftest_index = try expectSingleTrimmedLine(workflow, workflow_alignment_selftest);
    const alignment_check_index = try expectSingleTrimmedLine(workflow, workflow_alignment_check);
    const make_cross_index = try expectSingleTrimmedLine(workflow, workflow_make_cross);

    try expectAscending(&.{
        direct_selftest_index,
        direct_check_index,
        alignment_selftest_index,
        alignment_check_index,
        make_cross_index,
    });
}

test "bootstrap workflow validates required routes after running phase2-cross" {
    const workflow = try readRepoFile(workflow_path, 256 * 1024);
    defer std.testing.allocator.free(workflow);

    const make_cross_index = try expectSingleTrimmedLine(workflow, workflow_make_cross);
    const required_routes_selftest_index = try expectSingleTrimmedLine(workflow, workflow_required_routes_selftest);
    const required_routes_check_index = try expectSingleTrimmedLine(workflow, workflow_required_routes_check);
    const make_validate_index = try expectSingleTrimmedLine(workflow, workflow_make_validate);
    const make_phase2_index = try expectSingleTrimmedLine(workflow, workflow_make_phase2);

    try expectAscending(&.{
        make_cross_index,
        required_routes_selftest_index,
        required_routes_check_index,
        make_validate_index,
        make_phase2_index,
    });
}

test "Makefile keeps phase2-cross wired into the aggregate dependency chain" {
    const makefile = try readRepoFile(makefile_path, 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const cross_target_index = try expectSingleTrimmedLine(makefile, makefile_cross_target);
    const direct_selftest_index = try expectSingleTrimmedLine(makefile, makefile_direct_selftest);
    const direct_check_index = try expectSingleTrimmedLine(makefile, makefile_direct_check);
    const alignment_selftest_index = try expectSingleTrimmedLine(makefile, makefile_alignment_selftest);
    const alignment_check_index = try expectSingleTrimmedLine(makefile, makefile_alignment_check);

    try expectAscending(&.{
        cross_target_index,
        direct_selftest_index,
        direct_check_index,
        alignment_selftest_index,
        alignment_check_index,
    });
    try expectContains(makefile, makefile_validate_chain);
    try expectContains(makefile, makefile_phase2_chain);
}

test "policy and fixture keep the two-target direct cross boundary" {
    const policy = try readRepoFile(policy_path, 32 * 1024);
    defer std.testing.allocator.free(policy);
    const fixture = try readRepoFile(fixture_path, 32 * 1024);
    defer std.testing.allocator.free(fixture);

    try expectContains(policy, "\"archive_sha256\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(policy, "\"" ++ x86_target ++ "\"");
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, policy, "\"" ++ aarch64_target ++ "\":"));

    try expectContains(fixture, "\"route\": \"" ++ route ++ "\"");
    try expectContains(fixture, "\"target\": \"" ++ x86_target ++ "\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"" ++ aarch64_target ++ "\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, fixture, "riscv64-linux"));
}
