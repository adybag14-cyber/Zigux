const std = @import("std");
const testing = std.testing;

const default_validator_path = "scripts/zigux/validate-phase1-closure.py";

fn readValidatorSource() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        default_validator_path,
        testing.allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var remaining = haystack;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        count += 1;
        remaining = remaining[index + needle.len ..];
    }

    try testing.expectEqual(expected, count);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierNeedleMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterNeedleMissing;
    try testing.expect(earlier_index < later_index);
}

test "phase1 closure validator normal success envelope stays explicit" {
    const validator = try readValidatorSource();
    defer testing.allocator.free(validator);

    try expectCount(validator, "PHASE1_CLOSURE_VALIDATION=pass", 1);
    try expectCount(validator, "PHASE1_CLOSURE_MODE=current-master-safe", 1);
    try expectContains(validator, "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
    try expectContains(validator, "print(\"PHASE1_CLOSURE_MODE=current-master-safe\")");
}

test "phase1 closure validator keeps normal success outside self test output" {
    const validator = try readValidatorSource();
    defer testing.allocator.free(validator);

    try expectContains(validator, "if args.self_test:");
    try expectContains(validator, "return run_self_test()");
    try expectContains(validator, "PHASE1_CLOSURE_SELF_TEST=pass");
    try expectNotContains(validator, "PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass");
    try expectOrdered(validator, "if args.self_test:", "failures = collect_failures(repo_root(args.root))");
    try expectOrdered(validator, "return run_self_test()", "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
}

test "phase1 closure validator prints normal success only after fail-closed checks" {
    const validator = try readValidatorSource();
    defer testing.allocator.free(validator);

    try expectContains(validator, "failures = collect_failures(repo_root(args.root))");
    try expectContains(validator, "if failures:");
    try expectContains(validator, "for failure in failures:");
    try expectContains(validator, "return 1");
    try expectOrdered(validator, "failures = collect_failures(repo_root(args.root))", "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
    try expectOrdered(validator, "for failure in failures:", "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
    try expectOrdered(validator, "return 1", "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
}
